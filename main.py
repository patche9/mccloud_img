from astrbot.api.message_components import *
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
import aiohttp

@register("mccloud_img", "MC云-小馒头", "从API获取随机图片。使用 /来点涩图 获取一张随机图片，可添加多个tag筛选。", "1.0")
class SetuPlugin(Star):
    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.config = config
        self.api_url = config.get("api_url", "")

    @filter.command("来点涩图")
    async def get_setu(self, event: AstrMessageEvent):
        if not self.api_url:
            yield event.plain_result("\n请先在配置文件中设置API地址")
            return
        
        # 解析用户输入的tag参数
        args = event.message_str.split()[1:]  # 分割命令后的参数
        params = [('tag', tag) for tag in args]  # 构造查询参数

        ssl_context = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.ClientSession(connector=ssl_context) as session:
            try:
                # 发送带参数的GET请求
                async with session.get(self.api_url, params=params) as response:
                    data = await response.json()
                    
                    if data["error"]:
                        yield event.plain_result(f"\n获取图片失败：{data['error']}")
                        return
                    
                    if not data["data"]:
                        yield event.plain_result("\n未找到符合标签的图片")
                        return
                    
                    image_data = data["data"][0]
                    image_url = image_data["urls"]["original"]
                    
                    chain = [Image.fromURL(image_url)]
                    yield event.chain_result(chain)
                    
            except Exception as e:
                yield event.plain_result(f"\n请求失败: {str(e)}")
