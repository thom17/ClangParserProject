import re
from collections import Counter
from typing import List

from oms.info_set import InfoSet
from oms.dataset.info_base import InfoBase, CoreInfoData

class FunctionInfo(InfoBase):
    def __init__(self, core_info: CoreInfoData, owner: InfoBase = None):
        self.parameters: [InfoBase] = []

        super().__init__(core_info, owner)

    @classmethod
    def from_dict(cls, di: dict, owner: InfoBase = None) -> 'FunctionInfo':
        core_info = CoreInfoData.from_dict(di)
        return cls(core_info, owner)

    @staticmethod
    def _split_words(text: str) -> List[str]:
        if not text:
            return []

        normalized = text.replace('::', ' ').replace('.', ' ').replace('~', ' Destructor ')
        normalized = re.sub(r'[^0-9A-Za-z_]+', ' ', normalized)
        normalized = re.sub(r'([a-z])([A-Z])', r'\1 \2', normalized)
        normalized = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', normalized)
        normalized = normalized.replace('_', ' ')
        return [word for word in normalized.split() if word]

    @staticmethod
    def _to_tag(word: str) -> str | None:
        cleaned = re.sub(r'[^0-9A-Za-z]', '', word)
        if len(cleaned) < 2:
            return None

        upper = cleaned.upper()
        if upper in {
            'C', 'VOID', 'BOOL', 'INT', 'FLOAT', 'DOUBLE', 'CHAR', 'TRUE', 'FALSE',
            'NULL', 'THIS', 'CONST', 'AUTO', 'RETURN', 'CLASS', 'STRUCT'
        }:
            return None

        if cleaned.isupper() and len(cleaned) <= 5:
            return cleaned

        return cleaned[0].upper() + cleaned[1:]

    def generate_hashtags(self, limit: int = 8) -> List[str]:
        scores = Counter()

        def add_tag(tag: str | None, score: int):
            '''
            score : 태그 중요도 점수 limit (개수 까지만 출력하므로))
            '''
            if tag:
                scores[tag] += score

        name_words = self._split_words(self.name)
        src_words = self._split_words(self.src_name)
        type_words = self._split_words(self.type_str)
        path_words = self._split_words(self.file_path)
        comment_words = self._split_words(self.comment)
        code_identifiers = re.findall(r'[A-Za-z_][A-Za-z0-9_]*', self.code or '')

        for word in name_words:
            add_tag(self._to_tag(word), 6)
        for word in src_words:
            add_tag(self._to_tag(word), 4)
        for word in type_words:
            add_tag(self._to_tag(word), 3)
        for word in path_words[-6:]:
            add_tag(self._to_tag(word), 1)
        for word in comment_words:
            add_tag(self._to_tag(word), 2)

        for identifier in code_identifiers:
            for word in self._split_words(identifier):
                add_tag(self._to_tag(word), 1)

        lower_name = self.name.lower()
        lower_code = (self.code or '').lower()

        if self.name == self.owner.name if self.owner else False:
            add_tag('Constructor', 8)
        if self.name.startswith('~'):
            add_tag('Destructor', 8)
            add_tag('Cleanup', 5)
        if self.is_static:
            add_tag('Static', 5)
        if self.is_virtual:
            add_tag('Virtual', 5)

        role_rules = {
            'get': 'Getter',
            'set': 'Setter',
            'is': 'StateCheck',
            'has': 'StateCheck',
            'create': 'Creation',
            'make': 'Creation',
            'init': 'Initialization',
            'update': 'Update',
            'draw': 'Rendering',
            'render': 'Rendering',
            'load': 'Loading',
            'save': 'Saving',
            'parse': 'Parsing',
            'convert': 'Conversion',
            'validate': 'Validation',
            'on': 'EventHandler',
        }
        for prefix, tag in role_rules.items():
            if lower_name.startswith(prefix):
                add_tag(tag, 6)

        code_rules = {
            'delete': 'Cleanup',
            'destroy': 'Cleanup',
            'render': 'Rendering',
            'draw': 'Rendering',
            'load': 'Loading',
            'save': 'Saving',
            'update': 'Update',
            'create': 'Creation',
            'camera': 'Camera',
            'image': 'Image',
            'font': 'Font',
            'json': 'Json',
            'xml': 'Xml',
            'parse': 'Parsing',
        }
        for keyword, tag in code_rules.items():
            if keyword in lower_code:
                add_tag(tag, 3)

        hashtags: List[str] = []
        for tag, _score in scores.most_common():
            hashtag = f'#{tag}'
            if hashtag not in hashtags:
                hashtags.append(hashtag)
            if len(hashtags) >= limit:
                break

        return hashtags
    
if __name__ == "__main__":
    from oms.parse_manager import ParseManager
    manager = ParseManager(r'D:\dev\AutoPlanning\trunk\Ap-Trunk-Auto-Task')
    manager.smart_parse_project()
    for file_info in manager.db.load_all():
        for fn_info in file_info.info_set.functionInfos.values():
            print(f"{fn_info.src_name} : {fn_info.generate_hashtags(limit=8)}")
