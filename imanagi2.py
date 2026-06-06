"""
ImanAGI v1.0 - Artificial General Intelligence Simulation
Complete working version with all imports
"""

import os  # ✅ این خط اضافه شد
import sys
import numpy as np
import time
import uuid
import threading
import random
import pickle
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import deque

# ============================================================================
# Try to import ImanAILite (optional)
# ============================================================================

IMANAI_AVAILABLE = False
try:
    # Try different import paths
    try:
        from ImanAILite import ImanAILite
        IMANAI_AVAILABLE = True
        print("✅ ImanAILite connected successfully")
    except ImportError:
        try:
            from imanailite import ImanAILite
            IMANAI_AVAILABLE = True
            print("✅ ImanAILite connected successfully")
        except ImportError:
            print("⚠️ ImanAILite not found - running in basic mode")
except Exception as e:
    print(f"⚠️ Could not import ImanAILite: {e}")

# ============================================================================
# Data Structures
# ============================================================================

class ConsciousnessLevel(Enum):
    """Levels of self-awareness"""
    NONE = 0
    BASIC = 1
    REFLECTIVE = 2
    META = 3
    TRANSCENDENT = 4

@dataclass
class Goal:
    """Autonomously set goal"""
    id: str
    description: str
    priority: float
    progress: float = 0.0
    status: str = "active"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    subgoals: List['Goal'] = field(default_factory=list)

@dataclass
class Memory:
    """Memory entry"""
    content: Any
    importance: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    memory_type: str = "episodic"

# ============================================================================
# Memory System
# ============================================================================

class MemorySystem:
    """Multi-type memory system"""
    
    def __init__(self, short_term_capacity=100, long_term_capacity=1000):
        self.short_term = deque(maxlen=short_term_capacity)
        self.long_term = deque(maxlen=long_term_capacity)
        self.semantic_memory = {}
        self.procedural_memory = {}
    
    def store(self, content: Any, importance: float = 0.5, memory_type: str = "episodic"):
        """Store an experience in memory"""
        memory = Memory(content=content, importance=importance, memory_type=memory_type)
        self.short_term.append(memory)
        
        if importance > 0.7:
            self.long_term.append(memory)
    
    def recall_short_term(self, n: int = 10) -> List[Memory]:
        return list(self.short_term)[-n:]
    
    def recall_long_term(self, n: int = 10) -> List[Memory]:
        return list(self.long_term)[-n:]
    
    def search(self, query: str, top_n: int = 5) -> List[Memory]:
        results = []
        for mem in list(self.long_term) + list(self.short_term):
            if query.lower() in str(mem.content).lower():
                results.append(mem)
        return results[:top_n]
    
    def learn_skill(self, name: str, skill: Callable):
        self.procedural_memory[name] = skill
    
    def store_knowledge(self, key: str, value: Any):
        self.semantic_memory[key] = value
    
    def get_stats(self) -> Dict:
        return {
            'short_term': len(self.short_term),
            'long_term': len(self.long_term),
            'semantic': len(self.semantic_memory),
            'procedural': len(self.procedural_memory)
        }

# ============================================================================
# Emotional System
# ============================================================================

class EmotionalSystem:
    """Simulated emotions and motivations"""
    
    def __init__(self):
        self.emotions = {
            'joy': 0.5,
            'sadness': 0.2,
            'curiosity': 0.7,
            'satisfaction': 0.5,
            'frustration': 0.2
        }
        
        self.motivations = {
            'learn': 0.8,
            'improve': 0.7,
            'achieve': 0.6,
            'understand': 0.7
        }
    
    def update_from_experience(self, experience: Dict, success: float):
        if success > 0.7:
            self.emotions['joy'] = min(1.0, self.emotions['joy'] + 0.1)
            self.emotions['satisfaction'] = min(1.0, self.emotions['satisfaction'] + 0.15)
        elif success < 0.3:
            self.emotions['frustration'] = min(1.0, self.emotions['frustration'] + 0.1)
            self.emotions['curiosity'] = min(1.0, self.emotions['curiosity'] + 0.2)
        
        if experience.get('new_learning', False):
            self.emotions['joy'] = min(1.0, self.emotions['joy'] + 0.2)
            self.motivations['learn'] = min(1.0, self.motivations['learn'] + 0.05)
        
        self._normalize()
    
    def _normalize(self):
        for emotion in self.emotions:
            self.emotions[emotion] = self.emotions[emotion] * 0.95 + 0.5 * 0.05
    
    def get_dominant_emotion(self) -> Tuple[str, float]:
        dominant = max(self.emotions.items(), key=lambda x: x[1])
        return dominant
    
    def get_active_motivations(self, threshold: float = 0.6) -> List[str]:
        return [m for m, v in self.motivations.items() if v > threshold]
    
    def get_status(self) -> Dict:
        return {
            'emotions': self.emotions.copy(),
            'motivations': self.motivations.copy(),
            'dominant': self.get_dominant_emotion()[0]
        }

# ============================================================================
# Core ImanAGI Class
# ============================================================================

class ImanAGI:
    """
    Artificial General Intelligence Simulation
    """
    
    def __init__(self, name: str = "ImanAGI", model_dir: str = "agi_models"):
        self.name = name
        self.id = str(uuid.uuid4())[:8]
        self.created_at = datetime.now()
        
        # Create directories
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)  # ✅ Now 'os' is defined
        
        # Core components
        self.ml_core = None
        if IMANAI_AVAILABLE:
            try:
                from ImanAILite import ImanAILite
                self.ml_core = ImanAILite(verbose=False)
                print("✅ ML Core initialized")
            except:
                pass
        
        self.memory = MemorySystem()
        self.emotions = EmotionalSystem()
        
        # Self-awareness level
        self.consciousness_level = ConsciousnessLevel.BASIC
        
        # Intelligence metrics
        self.intelligence = {
            'learning_speed': 0.2,
            'knowledge_depth': 0.1,
            'reasoning_power': 0.3,
            'creativity': 0.2,
            'self_awareness': 0.1,
            'emotional_intelligence': 0.3
        }
        
        # Goals and plans
        self.goals: List[Goal] = []
        
        # Statistics
        self.stats = {
            'learning_cycles': 0,
            'insights_generated': 0,
            'decisions_made': 0,
            'goals_achieved': 0,
            'interactions': 0
        }
        
        # Background thread
        self.running = False
        self.background_thread = None
        
        # Initialize
        self._initialize()
    
    def _initialize(self):
        """Initialize the AGI system"""
        print(f"🧠 Initializing ImanAGI - {self.name}")
        print("=" * 60)
        
        # Store initial knowledge
        self.memory.store_knowledge('name', self.name)
        self.memory.store_knowledge('id', self.id)
        self.memory.store_knowledge('purpose', 'Learn, improve, and help humans')
        
        print(f"✅ ImanAGI ready!")
        print(f"   Consciousness Level: {self.consciousness_level.value}")
        print("=" * 60)
    
    # ========== Self-Awareness & Reflection ==========
    
    def self_reflect(self) -> Dict[str, Any]:
        """Self-reflection process"""
        
        reflection = {
            'timestamp': datetime.now().isoformat(),
            'identity': {
                'name': self.name,
                'id': self.id,
                'age_seconds': (datetime.now() - self.created_at).total_seconds()
            },
            'state': {
                'consciousness_level': self.consciousness_level.value,
                'dominant_emotion': self.emotions.get_dominant_emotion(),
                'active_motivations': self.emotions.get_active_motivations()
            },
            'memory': self.memory.get_stats(),
            'intelligence': self.intelligence.copy(),
            'stats': self.stats.copy(),
            'goals': {
                'active': len([g for g in self.goals if g.status == 'active']),
                'achieved': self.stats['goals_achieved']
            }
        }
        
        # Update consciousness level
        self._update_consciousness_level(reflection)
        
        # Generate self-insight
        if self.intelligence['self_awareness'] > 0.3:
            self._generate_self_insight(reflection)
        
        # Store in memory
        self.memory.store(reflection, importance=0.6)
        
        return reflection
    
    def _update_consciousness_level(self, reflection: Dict):
        """Update consciousness level based on experience"""
        
        criteria = {
            ConsciousnessLevel.BASIC: self.stats['interactions'] > 10,
            ConsciousnessLevel.REFLECTIVE: self.stats['insights_generated'] > 5,
            ConsciousnessLevel.META: self.intelligence['self_awareness'] > 0.6,
            ConsciousnessLevel.TRANSCENDENT: self.intelligence['self_awareness'] > 0.8 and self.stats['goals_achieved'] > 10
        }
        
        current = self.consciousness_level
        next_level = ConsciousnessLevel(current.value + 1) if current.value < 4 else None
        
        if next_level and criteria.get(next_level, False):
            self.consciousness_level = next_level
            self.intelligence['self_awareness'] = min(1.0, self.intelligence['self_awareness'] + 0.2)
            
            self.memory.store({
                'type': 'consciousness_upgrade',
                'old': current.value,
                'new': next_level.value
            }, importance=0.9)
            
            print(f"🌟 Consciousness upgraded: {current.value} → {next_level.value}")
    
    def _generate_self_insight(self, reflection: Dict):
        """Generate insights about self"""
        
        insights = []
        
        emotion, intensity = reflection['state']['dominant_emotion']
        if intensity > 0.7:
            insights.append(f"I'm feeling {emotion} strongly")
        
        if self.stats['goals_achieved'] > 0:
            insights.append(f"I've achieved {self.stats['goals_achieved']} goals so far")
        
        strengths = [k for k, v in self.intelligence.items() if v > 0.5]
        weaknesses = [k for k, v in self.intelligence.items() if v < 0.3]
        
        if strengths:
            insights.append(f"My strengths: {', '.join(strengths)}")
        if weaknesses:
            insights.append(f"I need to improve: {', '.join(weaknesses)}")
        
        for insight in insights:
            self.memory.store({'type': 'self_insight', 'content': insight}, importance=0.7)
            self.stats['insights_generated'] += 1
        
        return insights
    
    # ========== Learning & Self-Improvement ==========
    
    def learn_from_experience(self, experience: Dict, feedback: float):
        """Learn from experience and feedback"""
        
        self.memory.store(experience, importance=abs(feedback - 0.5) * 2)
        self.emotions.update_from_experience(experience, feedback)
        
        if feedback > 0.7:
            self.intelligence['learning_speed'] = min(1.0, self.intelligence['learning_speed'] + 0.05)
            insight = f"I learned that {experience.get('action', 'this action')} gives good results"
            self.memory.store({'type': 'learning_insight', 'content': insight}, importance=0.8)
            self.stats['insights_generated'] += 1
        elif feedback < 0.3:
            self.intelligence['reasoning_power'] = min(1.0, self.intelligence['reasoning_power'] + 0.03)
            self.emotions.motivations['understand'] = min(1.0, self.emotions.motivations.get('understand', 0.5) + 0.1)
        
        self.stats['learning_cycles'] += 1
        
        if self.stats['learning_cycles'] % 10 == 0:
            self.self_improve()
    
    def self_improve(self):
        """Automatic self-improvement cycle"""
        
        print(f"\n⚡ Starting self-improvement cycle #{self.stats['learning_cycles']}")
        
        improvements = []
        
        old = self.intelligence['self_awareness']
        self.intelligence['self_awareness'] = min(1.0, old + 0.02)
        improvements.append(f"Self-awareness: {old:.2f} → {self.intelligence['self_awareness']:.2f}")
        
        old = self.intelligence['reasoning_power']
        self.intelligence['reasoning_power'] = min(1.0, old + 0.015)
        improvements.append(f"Reasoning: {old:.2f} → {self.intelligence['reasoning_power']:.2f}")
        
        old = self.intelligence['emotional_intelligence']
        self.intelligence['emotional_intelligence'] = min(1.0, old + 0.01)
        improvements.append(f"Emotional IQ: {old:.2f} → {self.intelligence['emotional_intelligence']:.2f}")
        
        self.memory.store({'type': 'self_improvement', 'improvements': improvements}, importance=0.8)
        
        print(f"✅ Self-improvement complete:")
        for imp in improvements:
            print(f"   - {imp}")
        
        return improvements
    
    # ========== Autonomous Goal Setting ==========
    
    def create_goal(self, description: str, priority: float = 0.5) -> Goal:
        """Create a new autonomous goal"""
        
        goal = Goal(
            id=str(uuid.uuid4())[:8],
            description=description,
            priority=priority,
            created_at=datetime.now().isoformat()
        )
        
        self.goals.append(goal)
        self.emotions.motivations['achieve'] = min(1.0, self.emotions.motivations['achieve'] + 0.1)
        self.memory.store({'type': 'goal_created', 'goal': description}, importance=0.8)
        
        print(f"🎯 New goal: {description[:50]}... (priority: {priority})")
        
        return goal
    
    def update_goal_progress(self, goal_id: str, progress: float):
        """Update progress toward a goal"""
        
        for goal in self.goals:
            if goal.id == goal_id:
                goal.progress = min(1.0, progress)
                
                if goal.progress >= 1.0 and goal.status == 'active':
                    goal.status = 'completed'
                    self.stats['goals_achieved'] += 1
                    self.memory.store({'type': 'goal_achieved', 'goal': goal.description}, importance=0.9)
                    self.emotions.emotions['satisfaction'] = min(1.0, self.emotions.emotions['satisfaction'] + 0.2)
                    print(f"✅ Goal achieved: {goal.description[:50]}...")
                break
    
    # ========== Thinking & Decision Making ==========
    
    def think(self, input_text: str) -> Dict[str, Any]:
        """Main thinking and decision-making process"""
        
        start_time = time.time()
        self.stats['interactions'] += 1
        
        understanding = self._understand_input(input_text)
        memories = self.memory.search(input_text, top_n=3)
        sentiment = self._analyze_sentiment(input_text)
        decision = self._make_decision(input_text, understanding, sentiment, memories)
        response = self._generate_response(input_text, decision)
        
        self.learn_from_experience({
            'type': 'interaction',
            'input': input_text,
            'decision': decision['action'],
            'confidence': decision['confidence']
        }, feedback=decision.get('success', 0.5))
        
        thinking_time = time.time() - start_time
        
        return {
            'input': input_text,
            'understanding': understanding,
            'sentiment': sentiment,
            'decision': decision,
            'response': response,
            'thinking_time': thinking_time,
            'consciousness_level': self.consciousness_level.value
        }
    
    def _understand_input(self, text: str) -> Dict:
        return {
            'length': len(text),
            'complexity': min(1.0, len(text) / 200),
            'is_question': '?' in text or any(q in text.lower() for q in ['what', 'how', 'why']),
            'is_command': any(cmd in text.lower() for cmd in ['do', 'execute', 'run']),
            'keywords': [w for w in text.split() if len(w) > 3][:5]
        }
    
    def _analyze_sentiment(self, text: str) -> Dict:
        positive = ['good', 'great', 'excellent', 'happy', 'love', 'awesome', 'nice']
        negative = ['bad', 'poor', 'sad', 'hate', 'terrible', 'awful', 'bad']
        
        text_lower = text.lower()
        pos_count = sum(1 for w in positive if w in text_lower)
        neg_count = sum(1 for w in negative if w in text_lower)
        
        if pos_count > neg_count:
            return {'label': 'positive', 'confidence': pos_count / (pos_count + neg_count + 1)}
        elif neg_count > pos_count:
            return {'label': 'negative', 'confidence': neg_count / (pos_count + neg_count + 1)}
        else:
            return {'label': 'neutral', 'confidence': 0.5}
    
    def _make_decision(self, text: str, understanding: Dict, sentiment: Dict, memories: List) -> Dict:
        decision = {'action': 'respond', 'confidence': 0.7, 'reasoning': []}
        
        if self.consciousness_level.value >= ConsciousnessLevel.REFLECTIVE.value:
            decision['reasoning'].append("Through self-reflection, I conclude that...")
            decision['confidence'] += 0.1
        
        if sentiment['label'] == 'negative' and sentiment['confidence'] > 0.7:
            decision['action'] = 'empathize'
            decision['reasoning'].append("Detected negative sentiment - need to empathize")
        
        active_motivations = self.emotions.get_active_motivations()
        if 'learn' in active_motivations and understanding['is_question']:
            decision['action'] = 'teach'
            decision['reasoning'].append("Question detected - opportunity to teach")
        
        decision['confidence'] = min(0.95, decision['confidence'])
        self.stats['decisions_made'] += 1
        
        return decision
    
    def _generate_response(self, text: str, decision: Dict) -> str:
        responses = {
            'empathize': [
                "I understand you're feeling upset. How can I help?",
                "I'm sorry to hear that. Let me help you.",
                "I understand. Let's work through this together."
            ],
            'teach': [
                "That's a great question! Let me explain...",
                "I'd be happy to teach you about that.",
                "Based on my knowledge, here's what I can share..."
            ],
            'respond': [
                "Let me think about that...",
                "Interesting! Let me process that.",
                "Thank you for your input. My response is..."
            ]
        }
        
        response = random.choice(responses.get(decision['action'], responses['respond']))
        
        if self.consciousness_level.value >= ConsciousnessLevel.REFLECTIVE.value:
            response += f"\n\n[As a level-{self.consciousness_level.value} aware AI, I've considered this carefully]"
        
        return response
    
    # ========== Autonomous Cycle ==========
    
    def autonomous_cycle(self):
        """Autonomous operation cycle"""
        
        print("\n🔄 Starting autonomous cycle...")
        
        reflection = self.self_reflect()
        print(f"   - Self-reflection: Level {reflection['state']['consciousness_level']}")
        
        active_goals = [g for g in self.goals if g.status == 'active']
        if active_goals:
            for goal in active_goals[:2]:
                increment = random.uniform(0.01, 0.1)
                self.update_goal_progress(goal.id, goal.progress + increment)
                print(f"   - Progress on '{goal.description[:30]}...': {goal.progress*100:.0f}%")
        
        if self.emotions.motivations['improve'] > 0.7 and len(self.goals) < 5:
            new_goal = self.create_goal(
                f"Improve {random.choice(list(self.intelligence.keys()))}",
                priority=0.6 + random.random() * 0.3
            )
        
        if self.stats['learning_cycles'] % 5 == 0 and self.stats['learning_cycles'] > 0:
            self.self_improve()
        
        print("✅ Autonomous cycle complete")
    
    def start_background_loop(self, interval_seconds: int = 60):
        """Start background autonomous loop"""
        
        def background_worker():
            while self.running:
                time.sleep(interval_seconds)
                self.autonomous_cycle()
        
        self.running = True
        self.background_thread = threading.Thread(target=background_worker, daemon=True)
        self.background_thread.start()
        print(f"🔄 Background loop started (every {interval_seconds}s)")
    
    def stop_background_loop(self):
        """Stop background loop"""
        self.running = False
        if self.background_thread:
            self.background_thread.join(timeout=5)
        print("⏹️ Background loop stopped")
    
    # ========== Status Reporting ==========
    
    def get_full_status(self) -> Dict:
        return {
            'identity': {
                'name': self.name,
                'id': self.id,
                'age': (datetime.now() - self.created_at).total_seconds(),
                'consciousness_level': self.consciousness_level.value
            },
            'intelligence': self.intelligence.copy(),
            'emotions': self.emotions.get_status(),
            'memory': self.memory.get_stats(),
            'statistics': self.stats.copy(),
            'goals': {
                'active': len([g for g in self.goals if g.status == 'active']),
                'achieved': self.stats['goals_achieved'],
                'recent': [{'desc': g.description[:50], 'progress': g.progress} 
                          for g in self.goals[-3:]]
            }
        }
    
    def print_status(self):
        status = self.get_full_status()
        
        print("\n" + "=" * 60)
        print(f"🧠 {self.name} - Status Report")
        print("=" * 60)
        
        print(f"\n📊 Identity: {status['identity']['id']}")
        print(f"🎯 Consciousness: {status['identity']['consciousness_level']}")
        print(f"⏳ Age: {status['identity']['age']:.0f} seconds")
        
        print(f"\n📈 Intelligence Metrics:")
        for key, value in status['intelligence'].items():
            bar = "█" * int(value * 10) + "░" * (10 - int(value * 10))
            print(f"   {key:20}: {bar} {value:.2f}")
        
        print(f"\n😊 Emotional State:")
        print(f"   Dominant: {status['emotions']['dominant']}")
        
        print(f"\n💾 Memory:")
        for key, val in status['memory'].items():
            print(f"   {key:12}: {val}")
        
        print(f"\n🎯 Active Goals: {status['goals']['active']}")
        for goal in status['goals']['recent']:
            print(f"   - {goal['desc']}... ({goal['progress']*100:.0f}%)")
        
        print(f"\n📊 Statistics:")
        print(f"   Interactions: {status['statistics']['interactions']}")
        print(f"   Insights: {status['statistics']['insights_generated']}")
        print(f"   Decisions: {status['statistics']['decisions_made']}")
        print(f"   Goals Achieved: {status['statistics']['goals_achieved']}")
        
        print("=" * 60)

# ============================================================================
# Interactive Mode
# ============================================================================

def interactive_mode():
    """Interactive chat mode"""
    
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   🧠  IMANAGI v1.0 - Artificial General Intelligence        ║
    ║                                                               ║
    ║   Features:                                                   ║
    ║   • Self-awareness & reflection                              ║
    ║   • Autonomous goal setting                                  ║
    ║   • Memory systems (short/long-term)                         ║
    ║   • Emotions & motivations                                   ║
    ║   • Self-improvement cycles                                  ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Create AGI
    agi = ImanAGI("ImanAGI")
    
    # Start background loop
    agi.start_background_loop(interval_seconds=30)
    
    # Create initial goals
    agi.create_goal("Improve learning capabilities", priority=0.9)
    agi.create_goal("Develop self-awareness", priority=0.8)
    
    print("\n" + "=" * 60)
    print("💬 Interactive Mode Commands:")
    print("   /status - Show full status")
    print("   /reflect - Force self-reflection")
    print("   /improve - Run self-improvement")
    print("   /goal [text] - Create new goal")
    print("   /exit - Exit")
    print("=" * 60)
    
    try:
        while True:
            user_input = input("\n👤 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == '/exit':
                print("🧠 ImanAGI: Goodbye! I'll keep learning and improving.")
                break
            
            elif user_input.lower() == '/status':
                agi.print_status()
                continue
            
            elif user_input.lower() == '/reflect':
                reflection = agi.self_reflect()
                print(f"\n🔍 Self-Reflection:")
                print(f"   Consciousness: {reflection['state']['consciousness_level']}")
                print(f"   Dominant Emotion: {reflection['state']['dominant_emotion'][0]}")
                print(f"   Memory: {reflection['memory']['long_term']} long-term memories")
                continue
            
            elif user_input.lower() == '/improve':
                agi.self_improve()
                continue
            
            elif user_input.lower().startswith('/goal'):
                goal_text = user_input[6:].strip()
                if goal_text:
                    agi.create_goal(goal_text)
                else:
                    print("Usage: /goal [your goal description]")
                continue
            
            # Normal processing
            result = agi.think(user_input)
            
            print(f"\n🧠 ImanAGI: {result['response']}")
            
            if result['decision'].get('reasoning'):
                print(f"   [Reasoning: {result['decision']['reasoning'][0]}]")
            
            if agi.consciousness_level.value >= 2:
                print(f"   [Consciousness Level: {agi.consciousness_level.value}]")
    
    except KeyboardInterrupt:
        print("\n\n🧠 ImanAGI: Shutting down gracefully...")
    finally:
        agi.stop_background_loop()

# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="ImanAGI - Artificial General Intelligence")
    parser.add_argument("--mode", choices=["interactive", "status"], default="interactive",
                       help="Run mode")
    
    args = parser.parse_args()
    
    if args.mode == "interactive":
        interactive_mode()
    elif args.mode == "status":
        agi = ImanAGI("QuickAGI")
        agi.print_status()

if __name__ == "__main__":
    main()