from __future__ import annotations
from model.character import Character


class Node:
    def __init__(self, character: Character, time: float):
        self.prev: Node = None
        self.next: Node = None
        self.time = time
        self.character = character

    def insert(self, pre: Node):
        if pre == None:
            return
        if pre.next is not None:
            pre.next.prev = self
        self.next = pre.next
        pre.next = self
        self.prev = pre

    def delete(self):
        if self.prev is not None:
            self.prev.next = self.next
        if self.next is not None:
            self.next.prev = self.prev
        del self


class Linked_list:
    def __init__(self):
        self.head: Node = None
        self.back: Node = None
        self.map: dict[int, Node] = dict()

    def delete(self, character: Character):
        if character.id in self.map:
            if self.map[character.id] is self.head:
                self.head = self.map[character.id].next
            if self.map[character.id] is self.back:
                self.back = self.map[character.id].prev
            self.map[character.id].delete()
            del self.map[character.id]

    def push_back(self, character: Character, time: float):
        self.map[character.id] = Node(character, time)
        if self.back is None:
            self.back = self.map[character.id]
            self.head = self.map[character.id]
        else:
            self.map[character.id].insert(self.back)

    def front(self):
        return self.head

    def back(self):
        return self.back
