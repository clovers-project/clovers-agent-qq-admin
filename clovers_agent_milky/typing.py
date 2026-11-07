from typing import TypedDict, Literal


class FriendRequest(TypedDict):
    time: int
    self_id: int
    post_type: Literal["request"]
    request_type: Literal["friend"]
    user_id: int
    comment: str
    flag: str
    via: str
