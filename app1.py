import threading
from bottle import Bottle, request, template, redirect
import schedule
import time
import asyncio
import aiohttp

app = Bottle()

tasks = []  # 存储任务信息的列表

@app.route('/')
def home():
    return template('index.html', tasks=tasks)

@app.route('/add_task', method='POST')
def add_task():
    url = request.forms.get('url')
    interval = int(request.forms.get('interval'))

    task = {
        'url': url,
        'interval': interval,
        'job': None,
        'paused': False
    }

    tasks.append(task)

    # 使用schedule库创建定时任务
    task['job'] = schedule.every(interval).seconds.do(run_task, task)

    return redirect('/')

@app.route('/remove_task/<index:int>', method='GET')
def remove_task(index):
    if index >= 0 and index < len(tasks):
        task = tasks[index]
        if task['job']:
            # 取消定时任务
            task['job'].cancel()
        del tasks[index]
        return redirect('/')
    else:
        return 'Invalid task index.'

@app.route('/pause_task/<index:int>', method='GET')
def pause_task(index):
    if index >= 0 and index < len(tasks):
        task = tasks[index]
        if task['job'] and not task['paused']:
            task['job'].pause()
            task['paused'] = True
        return redirect('/')
    else:
        return 'Invalid task index.'

@app.route('/resume_task/<index:int>', method='GET')
def resume_task(index):
    if index >= 0 and index < len(tasks):
        task = tasks[index]
        if task['job'] and task['paused']:
            task['job'].resume()
            task['paused'] = False
        return redirect('/')
    else:
        return 'Invalid task index.'

@app.route('/cancel_all_tasks', method='GET')
def cancel_all_tasks():
    for task in tasks:
        if task['job']:
            task['job'].cancel()
    tasks.clear()
    return redirect('/')

def run_task(task):
    # # 创建一个事件循环对象
    # loop = asyncio.get_event_loop()
    # # 将事件循环设置为当前线程的事件循环
    # asyncio.set_event_loop(loop)
    # asyncio.ensure_future(do_request(task))

    asyncio.set_event_loop(asyncio.new_event_loop())
    asyncio.get_event_loop().run_until_complete(do_request(task))

async def do_request(task):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(task['url']) as response:
                result = await response.text()
                print(f"URL: {task['url']}, Response: {result}")
        except aiohttp.ClientError as e:
            print(f"Error occurred while making request to {task['url']}: {str(e)}")

def start_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    # 启动调度器
    scheduler_thread = threading.Thread(target=start_scheduler)
    scheduler_thread.start()

    try:
        # 启动Bottle应用
        app.run(host='127.0.0.1', port=3000)
    finally:
        # 取消所有定时任务
        cancel_all_tasks()
