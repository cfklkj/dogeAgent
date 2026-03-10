"""
示例插件 - 笑话插件
"""
import random
from plugins.plugin_base import CommandPlugin

class JokePlugin(CommandPlugin):
    """笑话插件"""
    
    def __init__(self):
        super().__init__(
            plugin_id="joke_plugin",
            name="笑话大全",
            version="1.0.0"
        )
        
        # 注册命令
        self.register_command("笑话", self.tell_joke, "讲个笑话")
        self.register_command("冷笑话", self.tell_cold_joke, "讲个冷笑话")
        
        # 本地笑话库
        self.jokes = [
            "为什么程序员总是混淆万圣节和圣诞节？因为 Oct 31 等于 Dec 25！",
            "一只狗去便利店偷东西，被老板抓住了。老板问：你为什么要偷东西？狗说：我...我...我是狗急跳墙！",
            "小鱼问大鱼：大鱼大鱼，你最喜欢吃什么？大鱼说：我最喜欢吃小虾米。小鱼说：你虾啊？！"
        ]
        
        self.cold_jokes = [
            "一只企鹅去北极找北极熊玩，走了二十年终于到了，敲门说：北极熊在家吗？北极熊说：不在！",
            "一个番茄去面试，面试官问：你有什么特长？番茄说：我会变番茄酱。"
        ]
    
    async def initialize(self) -> bool:
        """初始化"""
        return True
    
    async def shutdown(self) -> bool:
        """关闭"""
        return True
    
    async def tell_joke(self, args: list, context: dict) -> str:
        """讲笑话"""
        joke = random.choice(self.jokes)
        return f"汪！讲个笑话给你听：\n\n{joke}\n\n😄"
    
    async def tell_cold_joke(self, args: list, context: dict) -> str:
        """讲冷笑话"""
        joke = random.choice(self.cold_jokes)
        return f"啊...好冷：\n\n{joke}\n\n❄️"
