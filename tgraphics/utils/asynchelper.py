import inspect

async def invoke(func, *args, **kwargs):
    obj = func(*args, **kwargs)
    if inspect.isawaitable(obj):
        return await obj
    return obj
