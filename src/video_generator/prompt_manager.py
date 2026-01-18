"""
火影忍者主题 Prompt 库
"""
from typing import List, Dict, Any
import random
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PromptManager:
    """Prompt 管理器，管理火影忍者主题的提示词库"""

    def __init__(self):
        self.prompts = {
            "character": self._get_character_prompts(),
            "jutsu": self._get_jutsu_prompts(),
            "scene": self._get_scene_prompts(),
            "battle": self._get_battle_prompts(),
            "emotional": self._get_emotional_prompts()
        }

    def _get_character_prompts(self) -> List[str]:
        """角色相关 Prompt"""
        return [
            "Naruto Uzumaki in his Hokage cloak standing on the Hokage faces monument, sunrise background, anime style, epic cinematic shot, high quality",
            "Sasuke Uchiha with his Rinnegan activated, lightning effects surrounding him, intense expression, dark atmosphere, anime style",
            "Sakura Haruno healing a wounded ninja with her Byakugo no Jutsu, soft green chakra glow, peaceful expression, anime style",
            "Kakashi Hatake reading his orange book while leaning against a tree, relaxed posture, Konoha forest background, anime style",
            "Itachi Uchiha using his Susanoo, red ethereal armor, dramatic lighting, intense battle scene, anime style",
            "Gaara in full sand armor, desert background, wind blowing sand, powerful stance, anime style",
            "Rock Lee with his gates opening, green aura surrounding him, intense training scene, anime style",
            "Hinata Hyuga using her Gentle Fist technique, Byakugan activated, precise movements, anime style",
            "Shikamaru Nara analyzing a battle situation, hands in pockets, calculating expression, sunset background, anime style",
            "Boruto Uzumaki using his Rasengan, blue chakra glow, determined expression, modern Konoha background, anime style"
        ]

    def _get_jutsu_prompts(self) -> List[str]:
        """忍术相关 Prompt"""
        return [
            "Naruto performing Rasengan, spinning blue chakra sphere in his palm, dynamic angle, energy particles, anime style",
            "Sasuke executing Chidori, lightning emanating from his hand, intense electrical effects, dramatic lighting, anime style",
            "Kakashi using Kamui, swirling vortex of energy, distortion of space-time, mysterious atmosphere, anime style",
            "Jiraiya summoning Gamabunta, giant toad emerging from smoke cloud, impressive scale, anime style",
            "Tsunade performing Creation Rebirth, green healing energy covering her body, transformation effect, anime style",
            "Hashirama using Wood Style Jutsu, massive forest growing from the ground, intricate tree patterns, anime style",
            "Madara Uchiha using his Eternal Mangekyo Sharingan, red patterns in eyes, powerful aura, anime style",
            "Naruto using Sage Mode, orange pigmentation around eyes, natural energy gathering, mountain background, anime style",
            "Minato Namikaze using Flying Raijin Jutsu, yellow flash of light, teleportation effect, anime style",
            "Obito Uchiha using Kamui, spiral dimension portal, dark void background, anime style"
        ]

    def _get_scene_prompts(self) -> List[str]:
        """场景相关 Prompt"""
        return [
            "Konohagakure village at sunset, peaceful atmosphere, Hokage faces monument in background, warm golden light, anime landscape style",
            "Forest of Death, ancient trees, mysterious atmosphere, filtered sunlight through leaves, anime environment style",
            "Akatsuki hideout, underground base, red clouds symbol, dark interior, anime style",
            "Valley of the End, giant stone statues of Hashirama and Madara, waterfall between them, epic landscape, anime style",
            "Mount Myoboku, toads practicing ninjutsu, misty mountain peaks, serene atmosphere, anime style",
            "Land of Iron samurai camp, snowy mountains, traditional Japanese architecture, winter atmosphere, anime style",
            "Hidden Sand Village, desert landscape, wind blowing sand, towering buildings, anime style",
            "Uchiha clan district at night, traditional houses, moonlit streets, nostalgic atmosphere, anime style",
            "Final Valley battle scene, waterfalls, destruction, dramatic lighting, intense atmosphere, anime style",
            "Ninja world at peace, different village symbols in sky, hopeful atmosphere, sunrise, anime style"
        ]

    def _get_battle_prompts(self) -> List[str]:
        """战斗相关 Prompt"""
        return [
            "Epic battle between Naruto and Sasuke at the Valley of the End, Rasengan vs Chidori clash, massive energy explosion, intense action, anime style",
            "Ninja war scene, thousands of shinobi fighting, jutsu explosions everywhere, epic scale, anime style",
            "Team 7 fighting together, coordinated attacks, dynamic teamwork, intense battle, anime style",
            "Madara Uchiha vs Five Kages, overwhelming power, devastating attacks, epic confrontation, anime style",
            "Naruto and Kurama in Perfect Tailed Beast Mode, giant fox form, energy projection, anime style",
            "Sasuke fighting against multiple opponents using his Susanoo, impenetrable defense, anime style",
            "Rock Lee vs Gaara tournament fight, sand armor vs taijutsu, intense speed, anime style",
            "Itachi vs Kisame, Amaterasu vs Samehada, elemental clash, anime style",
            "Naruto vs Pain, Six Paths of Pain, Rasenshuriken techniques, strategic battle, anime style",
            "Final battle scene, good vs evil, emotional climax, dramatic effects, anime style"
        ]

    def _get_emotional_prompts(self) -> List[str]:
        """情感相关 Prompt"""
        return [
            "Naruto remembering his parents, emotional scene, soft lighting, tears, nostalgic atmosphere, anime style",
            "Sasuke at the Uchiha clan massacre site, rain falling, dark mood, emotional expression, anime style",
            "Sakura thanking Naruto, sincere expression, warm colors, friendship moment, anime style",
            "Kakashi visiting Obito's grave, peaceful day, respectful posture, emotional weight, anime style",
            "Jiraiya saying goodbye to Naruto before his final mission, sunset, emotional farewell, anime style",
            "Naruto becoming Hokage ceremony, crowd cheering, proud expression, celebration, anime style",
            "Sasuke and Naruto fist bump at the Valley of the End, reconciliation moment, emotional climax, anime style",
            "Iruka praising Naruto for the first time, warm colors, mentor-student bond, anime style",
            "Hinata confessing to Naruto during the war, pink petals falling, romantic moment, anime style",
            "Naruto saying goodbye to Sasuke, tearful farewell, emotional scene, anime style"
        ]

    def get_random_prompt(self, category: str = None) -> str:
        """
        获取随机 Prompt

        Args:
            category: Prompt 类别 (character/jutsu/scene/battle/emotional)
                     如果为 None，则从所有类别中随机选择

        Returns:
            随机选择的 Prompt
        """
        if category and category in self.prompts:
            return random.choice(self.prompts[category])

        all_prompts = []
        for prompts in self.prompts.values():
            all_prompts.extend(prompts)

        return random.choice(all_prompts)

    def get_prompts_by_category(self, category: str) -> List[str]:
        """
        根据类别获取 Prompt 列表

        Args:
            category: Prompt 类别

        Returns:
            该类别的 Prompt 列表
        """
        return self.prompts.get(category, [])

    def get_multiple_prompts(self, count: int, category: str = None) -> List[str]:
        """
        获取多个随机 Prompt（不重复）

        Args:
            count: 要获取的数量
            category: Prompt 类别

        Returns:
            Prompt 列表
        """
        if category:
            available_prompts = self.prompts.get(category, []).copy()
        else:
            available_prompts = []
            for prompts in self.prompts.values():
                available_prompts.extend(prompts)

        if count > len(available_prompts):
            count = len(available_prompts)

        return random.sample(available_prompts, count)

    def get_custom_prompt(
        self,
        character: str = None,
        action: str = None,
        style: str = None,
        background: str = None
    ) -> str:
        """
        自定义生成 Prompt

        Args:
            character: 角色名称
            action: 动作描述
            style: 艺术风格
            background: 背景场景

        Returns:
            组合后的 Prompt
        """
        parts = []

        if character:
            parts.append(character)

        if action:
            parts.append(action)

        if background:
            parts.append(f"{background} background")

        parts.extend([
            "anime style",
            "high quality",
            "epic",
            "dramatic lighting"
        ])

        if style:
            parts.append(style)

        return ", ".join(parts)

    def add_custom_prompt(self, category: str, prompt: str):
        """
        添加自定义 Prompt

        Args:
            category: Prompt 类别
            prompt: 要添加的 Prompt
        """
        if category not in self.prompts:
            self.prompts[category] = []

        self.prompts[category].append(prompt)
        logger.info(f"Added custom prompt to category '{category}'")

    def get_all_categories(self) -> List[str]:
        """获取所有类别"""
        return list(self.prompts.keys())

    def get_prompt_count(self, category: str = None) -> int:
        """
        获取 Prompt 数量

        Args:
            category: 类别，如果为 None 则返回总数

        Returns:
            Prompt 数量
        """
        if category:
            return len(self.prompts.get(category, []))

        total = 0
        for prompts in self.prompts.values():
            total += len(prompts)

        return total
