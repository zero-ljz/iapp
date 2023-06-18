import threading
import time
from datetime import datetime
import schedule
import asyncio
import aiohttp
from bottle import Bottle, request, template, redirect
import logging

# 设置日志记录的配置
logging.basicConfig(filename='app2.log', level=logging.INFO)

app = Bottle()

tasks = []  # 存储任务信息的列表

def run_task(task):
    current_time = datetime.now()
    start_time = datetime.strptime(task['start_time'], "%Y-%m-%d %H:%M:%S")
    end_time = datetime.strptime(task['end_time'], "%Y-%m-%d %H:%M:%S")

    if start_time <= current_time <= end_time:
        # 添加日志记录
        logging.info(f"Executing task: {task['url']}")
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

def add_task(url, start_time, end_time, interval):
    task = {
        'url': url,
        'start_time': start_time,
        'end_time': end_time,
        'interval': interval,
        'job': None,
        'paused': False
    }

    tasks.append(task)

    # 使用 schedule 库创建定时任务
    task['job'] = schedule.every(interval).seconds.do(run_task, task)

def cancel_task(task):
    schedule.cancel_job(task['job'])
    tasks.remove(task)

    # 添加日志记录
    logging.info(f"Cancelled task: {task['url']}")

def pause_task(task):
    if task['job'] and not task['paused']:
        # task['job'].pause()
        task['paused'] = True

        # 添加日志记录
        logging.info(f"Paused task: {task['url']}")

def resume_task(task):
    if task['job'] and task['paused']:
        # task['job'].resume()
        task['paused'] = False

        # 添加日志记录
        logging.info(f"Resumed task: {task['url']}")

@app.route('/')
def home():
    return template('index2.html', tasks=tasks)

@app.route('/add_task', method='GET')
def handle_add_task():
    url = request.query.get('url')
    start_time = request.query.get('formatted_start_time')
    print(start_time)
    end_time = request.query.get('formatted_end_time')
    days = int(request.query.get('days'))
    hours = int(request.query.get('hours'))
    minutes = int(request.query.get('minutes'))
    seconds = int(request.query.get('seconds'))

    interval = days * 24 * 60 * 60 + hours * 60 * 60 + minutes * 60 + seconds

    add_task(url, start_time, end_time, interval)

    return redirect('/')

@app.route('/cancel_task/<index:int>', method='GET')
def handle_cancel_task(index):
    if index >= 0 and index < len(tasks):
        task = tasks[index]
        cancel_task(task)
        return redirect('/')
    else:
        return 'Invalid task index.'

@app.route('/pause_task/<index:int>', method='GET')
def handle_pause_task(index):
    if index >= 0 and index < len(tasks):
        task = tasks[index]
        pause_task(task)
        return redirect('/')
    else:
        return 'Invalid task index.'

@app.route('/resume_task/<index:int>', method='GET')
def handle_resume_task(index):
    if index >= 0 and index < len(tasks):
        task = tasks[index]
        resume_task(task)
        return redirect('/')
    else:
        return 'Invalid task index.'

if __name__ == '__main__':
    # 启动调度器
    scheduler_thread = threading.Thread(target=start_scheduler)
    scheduler_thread.start()

    try:
        # 启动 Bottle 应用
        app.run(host='127.0.0.1', port=8000, debug=True, reloader=True)
    finally:
        # 取消所有定时任务
        for task in tasks:
            cancel_task(task)

    # 添加日志记录
    logging.info("Application stopped")
