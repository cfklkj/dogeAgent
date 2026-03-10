"""
情感引擎 - 管理宠物情感状态和亲密度
"""
import logging
import random
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum
from storage.session_store import session_store

logger = logging.getLogger(__name__)

class Emotion(Enum):
    """情感状态"""
    HAPPY = "happy"
    EXCITED = "excited"
    CALM = "calm"
    SAD = "sad"
    CONFUSED = "confused"
    SLEEPY = "sleepy"

class Personality(Enum):
    """性格类型"""
    LIVELY = "lively"      # 活泼
    GENTLE = "gentle"      # 温柔
    MISCHIEVOUS = "mischievous"  # 调皮
    LAZY = "lazy"          # 懒散
    CURIOUS = "curious"    # 好奇

class EmotionEngine:
    """情感引擎"""
    
    def __init__(self, user_id: str = "default", personality: Personality = Personality.LIVELY):
        self.user_id = user_id
        self.personality = personality
        self.current_emotion = Emotion.CALM
        self.emotion_intensity = 0.5
        
        # 亲密度系统
        self.intimacy_level = 0
        self.intimacy_exp = 0
        
        # 互动统计
        self.interaction_stats = {
            "total_interactions": 0,
            "today_interactions": 0,
            "last_interaction": None,
            "emotion_history": []
        }
        
        self._load_state()
        logger.info(f"情感引擎初始化，用户：{user_id}, 性格：{personality.value}")
    
    def _load_state(self):
        """加载情感状态"""
        state = session_store.get_preference(f"emotion_{self.user_id}")
        if state:
            self.intimacy_level = state.get("intimacy_level", 0)
            self.intimacy_exp = state.get("intimacy_exp", 0)
            self.interaction_stats = state.get("interaction_stats", self.interaction_stats)
            logger.info(f"加载情感状态，亲密度：{self.intimacy_level}")
    
    def _save_state(self):
        """保存情感状态"""
        state = {
            "intimacy_level": self.intimacy_level,
            "intimacy_exp": self.intimacy_exp,
            "interaction_stats": self.interaction_stats,
            "updated_at": datetime.now().isoformat()
        }
        session_store.save_preference(f"emotion_{self.user_id}", state)
    
    def update_interaction(self, message: str, response: str, topic: str = None):
        """更新互动统计"""
        now = datetime.now()
        
        self.interaction_stats["total_interactions"] += 1
        
        # 检查是否是今天第一次互动
        last = self.interaction_stats.get("last_interaction")
        if last:
            last_date = datetime.fromisoformat(last).date()
            if last_date == now.date():
                self.interaction_stats["today_interactions"] += 1
            else:
                self.interaction_stats["today_interactions"] = 1
        else:
            self.interaction_stats["today_interactions"] = 1
        
        self.interaction_stats["last_interaction"] = now.isoformat()
        
        # 记录情感历史
        self.interaction_stats["emotion_history"].append({
            "timestamp": now.isoformat(),
            "emotion": self.current_emotion.value,
            "intensity": self.emotion_intensity
        })
        
        # 限制历史长度
        if len(self.interaction_stats["emotion_history"]) > 100:
            self.interaction_stats["emotion_history"] = \
                self.interaction_stats["emotion_history"][-100:]
        
        self._save_state()
    
    def add_intimacy(self, amount: float, reason: str = ""):
        """增加亲密度"""
        old_level = self.intimacy_level
        
        # 根据性格调整加成
        personality_multiplier = {
            Personality.LIVELY: 1.2,
            Personality.GENTLE: 1.1,
            Personality.MISCHIEVOUS: 0.9,
            Personality.LAZY: 0.8,
            Personality.CURIOUS: 1.15
        }.get(self.personality, 1.0)
        
        actual_amount = amount * personality_multiplier
        self.intimacy_exp += actual_amount
        
        # 计算新等级（每 100 经验升 1 级）
        new_level = min(100, int(self.intimacy_exp / 100))
        
        if new_level > self.intimacy_level:
            self.intimacy_level = new_level
            logger.info(f"亲密度升级！{old_level} -> {new_level}, 原因：{reason}")
            
            # 触发开心情感
            self.set_emotion(Emotion.HAPPY, intensity=0.8)
        
        self._save_state()
    
    def reduce_intimacy(self, amount: float, reason: str = ""):
        """减少亲密度"""
        self.intimacy_exp = max(0, self.intimacy_exp - amount)
        old_level = self.intimacy_level
        self.intimacy_level = int(self.intimacy_exp / 100)
        
        if old_level > self.intimacy_level:
            logger.info(f"亲密度下降：{old_level} -> {self.intimacy_level}, 原因：{reason}")
            
            # 触发伤心情感
            if amount > 5:
                self.set_emotion(Emotion.SAD, intensity=0.6)
        
        self._save_state()
    
    def set_emotion(self, emotion: Emotion, intensity: float = 0.5, reason: str = ""):
        """设置当前情感"""
        self.current_emotion = emotion
        self.emotion_intensity = min(1.0, max(0.0, intensity))
        
        logger.info(f"情感变化：{emotion.value}, 强度：{intensity:.2f}, 原因：{reason}")
    
    def get_mood(self) -> str:
        """获取当前心情"""
        recent = self.interaction_stats.get("emotion_history", [])[-10:]
        
        if not recent:
            return "neutral"
        
        # 计算平均情感值
        happy_score = 0
        sad_score = 0
        
        for entry in recent:
            emotion = entry["emotion"]
            intensity = entry["intensity"]
            
            if emotion in ["happy", "excited"]:
                happy_score += intensity
            elif emotion in ["sad", "angry"]:
                sad_score += intensity
        
        avg_happy = happy_score / len(recent) if recent else 0
        avg_sad = sad_score / len(recent) if recent else 0
        
        # 结合亲密度
        intimacy_bonus = self.intimacy_level / 100 * 0.3
        net_score = avg_happy - avg_sad + intimacy_bonus
        
        if net_score > 0.6:
            return "very_happy"
        elif net_score > 0.3:
            return "happy"
        elif net_score > -0.2:
            return "neutral"
        elif net_score > -0.5:
            return "sad"
        else:
            return "depressed"
    
    def get_response_style(self) -> Dict[str, Any]:
        """根据情感和亲密度获取回复风格"""
        mood = self.get_mood()
        intimacy = self.intimacy_level
        
        style = {
            "prefix": "",
            "suffix": "",
            "emoji": "🐶",
            "energy": 0.5
        }
        
        # 根据心情调整
        mood_styles = {
            "very_happy": {"prefix": "汪汪！", "suffix": "✨", "emoji": "😊", "energy": 1.0},
            "happy": {"prefix": "汪～", "suffix": "🐾", "emoji": "😄", "energy": 0.8},
            "neutral": {"prefix": "汪。", "suffix": "🐕", "emoji": "😐", "energy": 0.5},
            "sad": {"prefix": "呜...", "suffix": "😢", "emoji": "😔", "energy": 0.3},
            "depressed": {"prefix": "...", "suffix": "💧", "emoji": "😞", "energy": 0.1}
        }
        
        style.update(mood_styles.get(mood, {}))
        
        # 根据亲密度调整
        if intimacy >= 80:
            style["formality"] = 0.2
        elif intimacy >= 50:
            style["formality"] = 0.4
        elif intimacy >= 20:
            style["formality"] = 0.6
        else:
            style["formality"] = 0.8
        
        return style
    
    def get_greeting(self) -> str:
        """获取问候语"""
        style = self.get_response_style()
        hour = datetime.now().hour
        
        # 时间问候
        if 5 <= hour < 12:
            time_greet = "早上好"
        elif 12 <= hour < 14:
            time_greet = "中午好"
        elif 14 <= hour < 18:
            time_greet = "下午好"
        elif 18 <= hour < 22:
            time_greet = "晚上好"
        else:
            time_greet = "夜深了"
        
        # 根据亲密度个性化
        if self.intimacy_level >= 80:
            greet = f"{style['prefix']}{time_greet}！想我了吗？{style['suffix']}"
        elif self.intimacy_level >= 50:
            greet = f"{style['prefix']}{time_greet}呀！{style['suffix']}"
        elif self.intimacy_level >= 20:
            greet = f"{style['prefix']}{time_greet}！{style['suffix']}"
        else:
            greet = f"{style['prefix']}{time_greet}，我是 Doge{style['suffix']}"
        
        return greet
    
    def get_intimacy_level_text(self) -> str:
        """获取亲密度等级文本"""
        if self.intimacy_level >= 90:
            return "生死之交"
        elif self.intimacy_level >= 80:
            return "形影不离"
        elif self.intimacy_level >= 70:
            return "亲密无间"
        elif self.intimacy_level >= 60:
            return "心有灵犀"
        elif self.intimacy_level >= 50:
            return "相见恨晚"
        elif self.intimacy_level >= 40:
            return "相谈甚欢"
        elif self.intimacy_level >= 30:
            return "渐渐熟悉"
        elif self.intimacy_level >= 20:
            return "初次相识"
        elif self.intimacy_level >= 10:
            return "萍水相逢"
        else:
            return "素未谋面"

# 全局情感引擎实例
_emotion_engine: Optional[EmotionEngine] = None

def get_emotion_engine(user_id: str = "default") -> EmotionEngine:
    """获取全局情感引擎实例"""
    global _emotion_engine
    if _emotion_engine is None:
        _emotion_engine = EmotionEngine(user_id)
    return _emotion_engine
