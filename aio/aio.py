import asyncio
import aiohttp
import logging
logging.basicConfig(level=logging.DEBUG)

async def co_fetch(url):
    """
    'async def'でコルーチン関数定義になります
        - corutineはイベントループ内で遅延実行されます
        - 'await $corutine' でIO待ちの間他のコルーチンに処理を譲ります
    """
    try:
        # "async with" はブロック脱出でリソース開放処理を行います. [response.release()]
        async with aiohttp.request("GET", url) as response:
            print("3. before await: url:{}".format(url))
            # "await $corutine" でIO待ちの間他のコルーチンに処理を譲ります
            html = await response.text()
            # 非同期IO処理可能になったら制御が戻ります
            print("4. after await: url:{} html:{} ...".format(url, html[:10].strip()))
            return url, html
    except Exception as e:
        print("try-except: [{}]".format(e))

print("1. create future by asyncio.wait()")
# asyncio.wait() は実行後に[done, pending]を返すFutureです。これは遅延実行オブジェクトです。
future_wait = asyncio.wait([
        # コルーチン関数を引数付きで呼び出すとコルーチンが返ります。これは遅延実行オブジェクトです。
        co_fetch('https://www.wikipedia.org/'),
        co_fetch('http://www.yahoo.com'),
        co_fetch('http://httpstat.us/200'),
        co_fetch('http://'), # 例外検証のためエラーを発生させます
    ])
print("2. do run_until_complete()")
# asyncioイベントループを作成し、・遅延実行オブジェクトを実行します。
done, pending = asyncio.get_event_loop().run_until_complete(future_wait)
# Futureオブジェクトから実行結果を取り出します
for future in done:
    res = future.result()
    if res:
        print("5. future: url:{} body:{} ...".format(res[0], res[1][:10]))

"""
実行結果例。
    $ python aio.py
    1. create future by asyncio.wait()
    2. do run_until_complete()
    DEBUG:asyncio:Using selector: KqueueSelector
    try-except: [Host could not be detected.]
    3. before await: url:http://httpstat.us/200
    4. after await: url:http://httpstat.us/200 html:200 OK ...
    3. before await: url:http://www.yahoo.com
    3. before await: url:https://www.wikipedia.org/
    4. after await: url:https://www.wikipedia.org/ html:<!DOCTYPE ...
    4. after await: url:http://www.yahoo.com html:<!DOCTYPE ...
    5. future: url:http://httpstat.us/200 body:200 OK ...
    5. future: url:http://www.yahoo.com body:<!DOCTYPE  ...
    5. future: url:https://www.wikipedia.org/ body:<!DOCTYPE  ...

実行モデル概要
-----------------------------------
1. コルーチン作成
2. イベントループにコルーチン(async def)を突っ込んで 処理開始
3. コルーチン内で 待ちが発生する処理が出たら await で他タスクに処理を譲る
4. シングルスレッド内で [corutine実行/await処理移譲] が繰り返されます

実行スタイルは javascriptのシングルスレッド/setTimeout()での処理譲渡モデルに近い.

用語
-----------------------------------
- async/await: 
  非同期処理を簡単に記述するための構文サポート。python3, C#, javascript(ES.next) などで採用されている
- ノンブロッキング/非同期IO: 
  同期IOではIO処理でブロックが発生しプロセスが停止するところを,
  ブロックする代わりに処理を他タスク(コルーチン)に譲ることで高速に処理される.
- コルーチン:
  明示的に他タスクに処理を譲る処理(await)を入れることで シングルスレッドで擬似/軽量マルチタスクを実現する.
  corutine は ["co"-routine: collaborative routine/協調ルーチン] だと考えるとよい.
  ノンプリエンプティブ(非横取り) マルチタスク、協調的マルチタスク方式. 
- マルチスレッド: 
  プリエンプティブ (横取り) マルチタスク.  
  時間分割により強制並列実行が行われる. 
  python async/await の世界はマルチスレッドではなくシングルスレッド実行. python asyncioランタイムは非スレッドセーフ関数が多いので実装時は注意すること

- "async for" は非同期イテレーションを行います

注意点
-------------------------------------

デバッグ
-------------------------------------
実行時にasyncioデバッグ環境変数を指定するとデバッグログが有効になります
$ env PYTHONASYNCIODEBUG=1 python script.py 
"""
