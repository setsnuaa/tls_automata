# 自动机
from typing import List, Dict, Tuple, Set, Iterator, Optional
from itertools import combinations, product
import hashlib
import pylstar.automata.Automata


class IncompleteInputVocabulary(BaseException):
    pass


class MultipleDefinitionForATransition(BaseException):
    pass


class DifferentInputVocabulary(BaseException):
    pass


class IndistinguishableSetOfAutomata(BaseException):
    pass


Path = List[Tuple[int, str]]
# 状态转移 [input_word, (output_state, output_words, colors)]
# colors代表路径是否合法
TransitionList = Dict[str, Tuple[int, List[str], Set[str]]]


# 判断消息是否发送，如果没发送返回true
def message_was_not_sent(path: Path, msg: str) -> bool:
    relevant_transitions = [sent_msg for _, sent_msg in path if sent_msg == msg]
    return len(relevant_transitions) == 0


def use_star(colors):
    return colors, len(colors) == 0


def use_star_and_prefer_green(colors):
    if "green" in colors:
        return ["green"], False
    return colors, len(colors) == 0


# 自动机
class Automaton:
    def __init__(self, input_vocabulary: Set[str]):
        # states = Dict[input_state, Dict[input_word, Tuple(output_state, output_words, colors)]]
        self.states: Dict[int, TransitionList] = {}
        self.input_vocabulary = input_vocabulary
        self.hash: Optional[bytes] = None

    def __str__(self):
        vocabulary = list(self.input_vocabulary)
        vocabulary.sort()
        result = [" ".join(vocabulary)]
        for state in sorted(self.states):
            for input_word in sorted(self.states[state]):
                output_state, output_words, _ = self.states[state][input_word]
                output_words_s = "+".join(output_words)
                result.append(
                    f"{state}, {output_state}, {input_word}, {output_words_s}"
                )
        return "\n".join(result)

    def compute_hash(self) -> bytes:
        if not self.hash:
            complete_automaton = self.reorder_states()
            automaton_repr = str(complete_automaton).encode("utf-8")
            self.hash = hashlib.md5(automaton_repr).digest()
        return self.hash

    def __eq__(self, other):
        return self.compute_hash() == other.compute_hash()

    # 添加状态
    def add_state(self, state: int):
        self.hash = None
        if state not in self.states:
            self.states[state] = {}

    # 添加某个状态状态转移
    # pylint: disable=too-many-arguments
    def add_transition(
            self,
            input_state: int,
            output_state: int,
            input_word: str,
            output_words: List[str],
            colors: Set[str] = None
    ):
        if input_word not in self.input_vocabulary and input_word != "*":
            raise IncompleteInputVocabulary(input_word, self.input_vocabulary)
        self.hash = None
        self.add_state(input_state)
        self.add_state(output_state)
        if not colors:
            colors = set()
        if input_word != "*":
            if input_word in self.states[input_state]:
                raise MultipleDefinitionForATransition(input_state, input_word)
            self.states[input_state][input_word] = (output_state, output_words, colors)
        else:
            # 如果在自动机的输入表里面，但是不在某个状态的输入表里面，也进行添加
            for word in self.input_vocabulary:
                if word not in self.states[input_state]:
                    self.states[input_state][word] = (output_state, output_words, colors)

    # 返回某个状态收到某条消息的状态转移
    # [output_state, output_words, colors]
    def follow_transition(self, state: int, msg: str):
        return self.states[state][msg]

    # 某个状态下收到一个消息序列，返回转移后的状态以及输出序列
    # 基于当前状态和当前输入确定下一个状态
    # 因此转移的过程就是根据输入序列，不断转移状态，最终到达最后一条消息对应的输出状态
    def run(self, msg_sequence: List[str], initial_state=0) -> Tuple[int, List[List[str]]]:
        current_state = initial_state
        output = []
        for msg in msg_sequence:
            current_state, output_words, _ = self.follow_transition(current_state, msg)
            output.append(output_words)
        return current_state, output

    def reorder_states(self):
        state_mapping = self.browse_automaton_and_build_mapping()
        return self.produce_automaton_from_state_mapping(state_mapping)

    # 根据初始状态图进行状态排序，确保初始状态为0，终止状态为状态中的最大值
    # 返回的是初始状态图中状态到排序后状态的映射关系
    def browse_automaton_and_build_mapping(self) -> Dict[int, int]:
        src_states_to_visit = [0]
        src_sink_states_to_visit: List[int] = []
        state_mapping = {}
        dst_current_state = 0
        processed_states = set([0])

        # 非sink状态
        while src_states_to_visit:
            src_current_state = src_states_to_visit.pop(0)
            state_mapping[src_current_state] = dst_current_state
            dst_current_state += 1

            for msg in sorted(self.states[src_current_state]):
                output_state, _, _ = self.states[src_current_state][msg]
                if output_state in processed_states:
                    continue
                processed_states.add(output_state)
                if self.is_sink_state(output_state):
                    src_sink_states_to_visit.append(output_state)
                else:
                    src_states_to_visit.append(output_state)

        # sink状态
        while src_sink_states_to_visit:
            src_current_state = src_sink_states_to_visit.pop(0)
            state_mapping[src_current_state] = dst_current_state
            dst_current_state += 1

        return state_mapping

    # 判断是否是sink-state
    # 表示状态机到达某个状态后不能转移到其他状态了，只能转移到它本身
    def is_sink_state(self, state):
        for output_state, _, _ in self.states[state].values():
            if output_state != state:
                return False
        return True

    # 建立状态机
    def produce_automaton_from_state_mapping(self, state_mapping):
        result = Automaton(self.input_vocabulary)
        for input_state in state_mapping:
            for input_word in self.input_vocabulary:
                output_state, output_words, colors = self.follow_transition(input_state, input_word)
                result.add_transition(state_mapping[input_state],
                                      state_mapping[output_state],
                                      input_word,
                                      output_words,
                                      colors)
        return result

    def remove_input_word(self, word_to_remove):
        new_vocabulary = self.input_vocabulary
        new_vocabulary.remove(word_to_remove)
        result = Automaton(new_vocabulary)
        # 遍历状态转移表
        for input_state, transitions in self.states.items():
            for input_word in transitions:
                if input_word == word_to_remove:
                    continue
                output_state, output_words, colors = transitions[input_word]
                result.add_transition(input_state,
                                      output_state,
                                      input_word,
                                      output_words,
                                      colors)
        return result.reorder_states()

    def contains_transition_with_received_msg(self, msg):
        for transitions in self.states.values():
            for _, output_words, _ in transitions.values():
                if msg in output_words:
                    return True
        return False

    def enumerate_paths_until_recv_msg(self, expected_msg: str) -> Iterator[Path]:
        yield from self._enumerate_paths_until_recv_msg(0, [], expected_msg)

    # dfs 查找目标信息
    # path是已访问节点
    def _enumerate_paths_until_recv_msg(
            self, state: int, path: Path, expected_msg: str
    ) -> Iterator[Path]:
        for sent_msg in self.states[state]:
            next_state, recv_msgs, _ = self.states[state][sent_msg]
            new_path = path + [(state, sent_msg)]
            previous_states = [link[0] for link in new_path]
            # 当前状态的下一个状态之前没有遍历过
            if next_state not in previous_states:
                if expected_msg in recv_msgs:
                    yield new_path
                else:
                    yield from self._enumerate_paths_until_recv_msg(next_state, new_path, expected_msg)

    # 根据抽象的正确路径找到状态机中的那条正确路径
    # 抽象路径类似TLS成功握手发送的那些消息类型
    def extract_happy_path(self, path: List[Tuple[str, Set[str]]]) -> Optional[Path]:
        automata_path: List[Path] = []
        # 从初始状态开始找正确的那条路径
        state = 0
        for sent_msg, expected_msgs in path:
            next_state, received_msgs, _ = self.follow_transition(state, sent_msg)
            automata_path.append((state, sent_msg))
            if expected_msgs:
                # 如果期望的消息中一条都没有收到
                if not set(received_msgs).intersection(expected_msgs):
                    return None
            state = next_state
        return automata_path

    # 对路径着色
    def color_path(self, path: Path, color: str):
        for state, sent_msg in path:
            _, _, colors = self.follow_transition(state, sent_msg)
            colors.add(color)

    def dot(self, dot_policy=None):
        states = []
        transitions = []
        # 遍历所有状态
        for state in sorted(self.states):
            states.append(self._dot_state(state))
            transitions_to_merge: Dict[str, List[str]] = {}
            starrable_transitions: Set[str] = set()
            # 遍历一个状态对应的所有路径
            for sent_msg in sorted(self.states[state]):
                self._register_transition(
                    transitions_to_merge,
                    starrable_transitions,
                    state,
                    sent_msg,
                    dot_policy,
                )
            transitions.extend(self._commit_transitions(transitions_to_merge, starrable_transitions))
        return "digraph {\n" + "\n".join(states + transitions) + "\n}\n"

    def _dot_state(self, state):
        if state == 0:
            shape = "doubleoctagon"
        elif self.is_sink_state(state):
            shape = "rectangle"
        else:
            shape = "ellipse"
        return f'"{state}" [shape={shape}];'

    def _register_transition(self,
                             transitions_to_merge: Dict[str, List[str]],
                             starrable_transitions,
                             state,
                             sent_msg,
                             dot_policy):
        next_state, recv_msgs, colors = self.states(state, sent_msg)
        # output_words之间用"+"连接
        recv_msgs_str = "+".join(recv_msgs)
        params = f'label="%s / {recv_msgs_str}"'
        if dot_policy:
            colors, starrable = dot_policy(colors)
        else:
            starrable = False

        lines_to_fill = []
        if colors:
            for color in sorted(colors):
                lines_to_fill.append(
                    f'"{state}" -> "{next_state}" [{params}, color="{color}", fontcolor="{color}"];'
                )
        else:
            lines_to_fill = [f'"{state}" -> "{next_state}" [{params}];']

        for line_to_fill in lines_to_fill:
            if starrable:
                starrable_transitions.add(line_to_fill)
            if line_to_fill not in transitions_to_merge:
                transitions_to_merge[line_to_fill] = []
            transitions_to_merge[line_to_fill].append(sent_msg)

    def _commit_transitions(self, transition_to_merge, starrable_transitions):
