import random

import api.prototype as api
from util import log_info

log_info("AI spam: spam message, and do nothing.")


def every_tick(interface: api.API):

    interface.send_chat(random.choice(["😔😔😔😔😔",
                                       "int main()\n{\n}",
                                       "Gap\n\n\n\n\njump",
                                       "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C\x0D\x0E\x0F\x10\x11\x12\x13\x14\x15\x16\x17",
                                       "\U0010FFFF",
                                       "我不知道",
                                       "幹???",
                                       "哥們，這條刪了唄，我是無所謂的，沒那麼容易破防的，真的，我不輕易破防，但是我一個朋友可能有點汗流浹背了，他不太舒服想睡了，當然不是我哈，我一直都是行的，以一個旁觀者的心態看吧，也不至於破防吧，就是想照顧下我朋友的感受，他有點破防了，還是建議刪了吧，當然刪不刪隨你，我是沒感覺的，就是為朋友感到不平罷了，也不是那麼輕易破防的，求你了，刪了唄"]))
