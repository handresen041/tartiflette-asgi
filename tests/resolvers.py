import asyncio
import typing
from queue import Empty, Queue

from starlette.requests import Request
from tartiflette import Resolver, Subscription

from ._utils import Dog, PubSub


@Resolver("Query.hello")
async def hello(parent: typing.Any, args: dict, context: dict, info: dict) -> str:
    name = args.get("name", "stranger")
    return "Hello " + name


@Resolver("Query.whoami")
async def resolve_whoami(
    parent: typing.Any, args: dict, context: dict, info: dict
) -> str:
    request: Request = context["req"]
    user = request.state.user
    return "a mystery" if user is None else user


@Resolver("Query.foo")
async def resolve_foo(parent: typing.Any, args: dict, context: dict, info: dict) -> str:
    get_foo = context.get("get_foo", lambda: "default")
    return get_foo()


@Subscription("Subscription.dogAdded")
async def on_dog_added(
    parent: typing.Any, args: dict, ctx: dict, info: dict
) -> typing.AsyncIterator[dict]:
    pubsub: PubSub = ctx["pubsub"]
    queue: Queue = Queue()

    @pubsub.on("dog_added")
    def on_dog(dog: Dog) -> None:
        queue.put(dog)

    while True:
        try:
            dog = queue.get_nowait()
        except Empty:
            await asyncio.sleep(0.01)
            continue
        else:
            queue.task_done()
            if dog is None:
                break
            yield {"dogAdded": dog._asdict()}
