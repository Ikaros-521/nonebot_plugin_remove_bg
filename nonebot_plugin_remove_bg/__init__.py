import nonebot
import aiohttp
from nonebot import on_command, on_message, on_shell_command
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import (
    Bot, 
    Event,
    GroupMessageEvent,
    Message,
    MessageSegment,
    MessageEvent,
    PrivateMessageEvent,
)
from nonebot.params import CommandArg, ShellCommandArgv
# from nonebot.rule import ArgumentParser, ParserExit

# 官网获取 https://www.remove.bg/api#remove-background
remove_bg_api_key = ""

# 获取env配置
try:
    nonebot.logger.debug(nonebot.get_driver().config.remove_bg_api_key)
    remove_bg_api_key = nonebot.get_driver().config.remove_bg_api_key
except:
    nonebot.logger.debug("REMOVE_BG_API_KEY配置缺失喵，不配置功能无法使用滴~")

catch_str = on_command("去背景", aliases={"rm_bg"})

@catch_str.handle()
async def _(state: T_State, arg: Message = CommandArg()):
    msg = arg
    if msg:
        state["src_img"] = msg
    pass


@catch_str.got("src_img", prompt="请发送需要去除背景的图片喵~")
async def _(bot: Bot, event: MessageEvent, state: T_State):
    # 信息源自 群聊或私聊
    msg_from = "group"
    # 判断消息类型
    if not isinstance(event, GroupMessageEvent):
        msg_from = "private"
        
    msg: Message = state["src_img"]
    # try:
    for msg_sag in msg:
        if msg_sag.type == "image":
            url = msg_sag.data["url"]
            # nonebot.logger.info(url)

            # 由于私聊的图片链接直接传给trace无法获取正确的图片，所以本地做了处理
            if msg_from == "group":
                img_data = await remove_by_url(url)
            else:
                img_data = await remove_by_img(url)
            # nonebot.logger.info(img_data)

            try:
                await catch_str.finish(Message(MessageSegment.image(file=img_data)))
            except (KeyError, TypeError, IndexError) as e:
                msg = '果咩，接口可能挂了喵'
                await catch_str.finish(Message(f'{msg}'), at_sender=True)
        else:
            await catch_str.finish("请发送图片喵~命令结束")


async def remove_by_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.remove.bg/v1.0/removebg",
            data={
                "size": "auto", # 最大输出图像分辨率 preview/full/auto
                "type": "auto", # 前景类型 auto/person/product/car
                "type_level": 1, # 检测到的前景类型的分类级别 none/1/2/latest
                "format": "png", # 结果图像格式 auto/png/jpg/zip
                "roi": "0% 0% 100% 100%", # 感兴趣区域 x1 y1 x2 y2
                "crop": "false", # 是否裁剪掉所有空白区域
                "position": "original", # 在图像画布中定位主题 center/original/从“0%”到“100%”的一个值(水平和垂直)或两个值(水平、垂直)
                "scale": "original", # 相对于图像总尺寸缩放主体 从“10%”到“100%”之间的任何值，也可以是“original”(默认)。缩放主体意味着“位置=中心”(除非另有说明)。
                "add_shadow": "false", # 是否向结果添加人工阴影
                "semitransparency": "true", # 结果中是否包含半透明区域
                "image_url": url
            },
            headers={
                "X-Api-Key": remove_bg_api_key
            }
        ) as resp:
            if resp.status == 200:
                return await resp.read()
            else:
                return False


async def remove_by_img(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            content = await resp.content.read()
            async with aiohttp.ClientSession() as session2:
                async with session2.post(
                    "https://api.remove.bg/v1.0/removebg",
                    data={
                        "size": "auto", # 最大输出图像分辨率 preview/full/auto
                        "type": "auto", # 前景类型 auto/person/product/car
                        "type_level": "1", # 检测到的前景类型的分类级别 none/1/2/latest
                        "format": "png", # 结果图像格式 auto/png/jpg/zip
                        "roi": "0% 0% 100% 100%", # 感兴趣区域 x1 y1 x2 y2
                        "crop": "false", # 是否裁剪掉所有空白区域
                        "position": "original", # 在图像画布中定位主题 center/original/从“0%”到“100%”的一个值(水平和垂直)或两个值(水平、垂直)
                        "scale": "original", # 相对于图像总尺寸缩放主体 从“10%”到“100%”之间的任何值，也可以是“original”(默认)。缩放主体意味着“位置=中心”(除非另有说明)。
                        "add_shadow": "false", # 是否向结果添加人工阴影
                        "semitransparency": "true", # 结果中是否包含半透明区域
                        "image_file": content
                    },
                    headers={
                        "X-Api-Key": remove_bg_api_key
                    }
                ) as resp2:
                    if resp2.status == 200:
                        return await resp2.read()
                    else:
                        return False
