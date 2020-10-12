import asyncio
#http 请求
import aiohttp
#python lxml包用于解析XML和html文件，可以使用xpath和css定位元素
from lxml import html
import jsonlines

etree = html.etree
queue = asyncio.Queue()

# 发送http请求，获取html信息
async def get_html_from_url(url):
    sem = asyncio.Semaphore(100)  # 并发数量限制
    async with sem:
        async with aiohttp.ClientSession(headers=None, cookies='') as session:
            async with session.get(url) as resp:
                if resp.status in [200, 201]:
                    #获取html信息
                    data = await resp.text()
                    # print(data)
                    return data

# 加载本地的url
async def get_url_from_JSON():

    with open('source.json', 'r+', encoding="utf8") as f:
        for item in jsonlines.Reader(f):
            content = item['url']
            await queue.put(content)

    print('*****队列长度:{}*****'.format(queue.qsize()))
    return

# 从队列中获取url，处理每条url获取标题、作者、内容等信息
async def get_result():

    if queue.qsize() != 0:
        url = await queue.get()
        html = await get_html_from_url(url)
        h = etree.HTML(html)
        title = h.xpath('//*[@id="j_core_title_wrap"]/h3/text()')
        author = h.xpath('//*[@id="j_p_postlist"]/div[1]/div[1]/ul/li[3]/a/text()')
        content = h.xpath("//*[contains(@id,'post_content_')]/text()")

        post = {
            'url': url,
            '标题': title[0],
            '作者': author[0],
            '内容': content[0],
        }

        new = "{}\n".format(post)
        return new
    else:
        print('队列已经为空了！')

# 保存到JSON文件中
async def save_to_JSON():
    try:
        p = await get_result()
    except IndexError :
        pass
    with open('result.json', 'a') as f:
        try:
            f.write(str(p))
        except UnboundLocalError:
            pass

# main
async def main():

    print('*****读取所有url*****')
    await get_url_from_JSON()
    print('*****开始爬取帖子*****')

    task = [asyncio.create_task(save_to_JSON()) for _ in range(0, queue.qsize() - 1)]
    await asyncio.wait(task)
    print('*****完成*****\n')


if __name__ == '__main__':
    pass
    asyncio.run(main())
