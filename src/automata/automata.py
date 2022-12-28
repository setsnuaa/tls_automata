# TLS自动机相关操作
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

    # 将状态机格式化输出
    # ------------------------------------------------------------------
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
        return f'"{state}" [shape={shape} label={state}];'

    def _register_transition(self,
                             transitions_to_merge: Dict[str, List[str]],
                             starrable_transitions,
                             state,
                             sent_msg,
                             dot_policy):
        next_state, recv_msgs, colors = self.states[state][sent_msg]
        # output_words之间用"+"连接
        recv_msgs_str = "+".join(recv_msgs)
        params = f'label="%s / {recv_msgs_str}"'
        if dot_policy:
            colors, starrable = dot_policy(colors)
        else:
            starrable = False

        # line_to_fill = "0" -> "1" [label="%s / recv_msgs_str"];
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

    def _commit_transitions(self, transitions_to_merge, starrable_transitions):
        star_line = None
        max_factor = 0
        for line_to_fill in transitions_to_merge:
            # sent_msgs的长度
            factor = len(transitions_to_merge[line_to_fill])
            if line_to_fill in starrable_transitions and factor > max_factor:
                max_factor = factor
                star_line = line_to_fill
        if max_factor <= 1:
            star_line = None

        for line_to_fill in transitions_to_merge:
            if line_to_fill == star_line:
                continue
            sent_msgs = transitions_to_merge[line_to_fill]
            sent_msgs_str = "-".join(sent_msgs)
            # line_to_fill = "0" -> "1" [label="%s / {recv_msgs_str}"] % sent_msgs_str
            # line_to_fill = "0" -> "1" [label="sent_msgs_str / recv_msgs_str"]
            yield line_to_fill % sent_msgs_str

        if star_line:
            # pylint: disable=consider-using-f-string
            yield star_line % "*"

    # ----------------------------------------------------------------------

    # 修改输入集，返回一个新的自动机
    def rename_input_vocabulary(self, mapping: Dict[str, str]):
        new_vocabulary = set()
        for word in self.input_vocabulary:
            if word in mapping:
                new_vocabulary.add(mapping[word])
            else:
                new_vocabulary.add(word)
        result = Automaton(new_vocabulary)

        for state, transitions in self.states.items():
            for word in transitions:
                if word in mapping:
                    sent_msg = mapping[word]
                else:
                    sent_msg = word
                output = transitions[word]
                result.add_transition(state, output[0], sent_msg, output[1], output[2])
        return result

    # 修改输出集
    def rename_output_vocabulary(self, mapping: Dict[str, str]):
        result = Automaton(self.input_vocabulary)
        result.input_vocabulary = self.input_vocabulary
        for state, transitions in self.states.items():
            for sent_msg, output in transitions.items():
                new_recv_msgs = []
                for word in output[1]:
                    if word in mapping:
                        new_recv_msgs.append(mapping[word])
                    else:
                        new_recv_msgs.append(word)
                result.add_transition(state, output[0], sent_msg, new_recv_msgs, output[2])
        return result

    # 合并状态 -------------------------------------------
    def minimize(self):
        states_to_merge = self._find_states_to_merge()
        # 不断合并
        while states_to_merge:
            for state_list in states_to_merge:
                self._merge_state(state_list)
            # 合并一轮之后不一定最小，再次查找是否有可以合并的状态
            # 直到不能合并为止
            states_to_merge = self._find_states_to_merge()
        return self

    def _find_states_to_merge(self):
        # behaviors = [key=状态表，value=可以合并的状态的集合]
        behaviors: Dict[str, List[int]] = {}
        for state, transitions in self.states.items():
            behavior = str(sorted(transitions.items()))
            # 如果有两个状态，它们的转移表相同，则可以合并
            if behavior not in behaviors:
                behaviors[behavior] = []
            behaviors[behavior].append(state)

        result = []
        for same_states_list in behaviors.values():
            if len(same_states_list) > 1:
                result.append(same_states_list)
        return result

    def _merge_state(self, state_list):
        # 将合并状态中的第一个状态作为合并后的状态
        # 因为会存在下一个状态也出现在合并状态中，所以需要先修改下一个状态
        # 之后将其他状态从状态表中删除
        merged_state = state_list.pop(0)
        for transitions in self.states.values():
            for sent_msg, output in transitions.items():
                next_state, recv_msgs, colors = output
                if next_state in state_list:
                    transitions[sent_msg] = merged_state, recv_msgs, colors
        for state in state_list:
            self.states.pop(state)

    # ----------------------------------------------------

    def compute_bdist(self):
        """
        Return b_dist (int), the distinguishing bound for the state machine,
        and a dictionary of state pairs/sequences leading to the bound.
        """
        nb_states = len(self.states)

        b_dist = 0
        b_pairs: Dict[str, List[str]] = {}

        for pair in combinations(range(nb_states), 2):
            break_var = False
            for loop_index in range(1, nb_states):
                if break_var:
                    break
                for word in product(sorted(self.input_vocabulary), repeat=loop_index):
                    output_words1 = self.run(list(word), initial_state=pair[0])[1]
                    output_words2 = self.run(list(word), initial_state=pair[1])[1]
                    if output_words1 != output_words2:
                        if b_dist <= loop_index:
                            b_dist = loop_index
                            b_pairs[f"({pair[0]}, {pair[1]})"] = list(word)
                        break_var = True
                        break

            if break_var:
                continue

        b_pairs = {k: v for (k, v) in b_pairs.items() if len(v) == b_dist}
        return b_dist, b_pairs


# 从L*算法的状态机转换成TLS状态机
def convert_from_pylstar(
        input_vocabulary: List[str], pylstar_automaton: pylstar.automata.Automata.Automata
) -> Automaton:
    automaton = Automaton(set(input_vocabulary))

    for input_state in pylstar_automaton.get_states():
        for transition in input_state.transitions:
            input_word, output_words = transition.label.split("/")
            input_word = input_word.strip()
            # "+"分隔，并且清除
            output_words = [m.strip() for m in output_words.split("+") if m.strip()]
            automaton.add_transition(
                int(input_state.name),
                int(transition.output_state.name),
                input_word,
                output_words,
            )

    return automaton.reorder_states()


# 加载TLS自动机-------------------------------------------------
def load_automaton(content: str) -> Automaton:
    lines = content.split("\n")
    input_vocabulary = [word.strip() for word in lines[0].split(" ")]
    automaton = Automaton(set(input_vocabulary))
    for line in lines[1:]:
        if not line.strip():
            continue
        input_state_s, output_state_s, input_word, output_words_s = line.split(",")
        input_state = int(input_state_s)
        output_state = int(output_state_s)
        input_word = input_word.strip()
        output_words = [m.strip() for m in output_words_s.split("+") if m.strip()]
        automaton.add_transition(input_state, output_state, input_word, output_words)
    return automaton


def load_automaton_from_file(filename: str) -> Automaton:
    with open(filename, encoding="utf-8") as automaton_file:
        content = automaton_file.read()
    return load_automaton(content)


# --------------------------------------------------------------


# 两个状态机的所有区分序列
def extract_distinguishes(
    automaton1:Automaton,automaton2:Automaton
)->List[List[str]]:
    if automaton1.input_vocabulary!=automaton2.input_vocabulary:
        raise DifferentInputVocabulary

    vocabulary=automaton1.input_vocabulary
    max_depth=max(len(automaton1.states),len(automaton2.states))
    distinguishing_sequences=[]

    # dfs
    def find_differences(current_sequence:List[str],state1:int,state2:int):
        if len(current_sequence)==max_depth-1:
            return

        for word in vocabulary:
            visited_sequence=current_sequence+[word]
            next_state1, recv_msgs1, _ = automaton1.states[state1][word]
            next_state2, recv_msgs2, _ = automaton2.states[state2][word]
            if recv_msgs1==recv_msgs2:
                if next_state1!=state1 or next_state2!=state2:
                    find_differences(visited_sequence,next_state1,next_state2)
            else:
                distinguishing_sequences.append(visited_sequence)

    find_differences([],0,0)
    return distinguishing_sequences


# 多个状态机的区分序列
def extract_pairwise_distinguishes(automatas: List[Automaton]) -> List[List[List[str]]]:
    distinguishes = []
    for index,automaton1 in enumerate(automatas):
        for automaton2 in automatas[index+1:]:
            distinguish=extract_distinguishes(automaton1, automaton2)
            if distinguish:
                distinguishes.append(distinguish)
    return distinguishes


# 合并区分序列
def cover_distinguishes(distinguishes: List[List[List[str]]]) -> List[List[str]]:
    def find_next_best_sequence(distinguishes: List[List[List[str]]]) -> List[str]:
        sequence_counts:Dict[str,int]={}


