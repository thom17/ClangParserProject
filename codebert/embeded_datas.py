'''
2024-09-27
OMS_MethodInfo를 임베딩시켜 처리하는건 어느정도 익숙? 해진듯 하다.
이를 활용하여 추가적인 데이터 파싱을 진행하기 위해 아래의 사항들을 고려해보았다.

1. dict, list 등의 단순데이터로 oms와 mapping
2. 주피터에서 간단하게 클래스를 정의하여 임베딩된 벡터와 OMS mapping
3. 기존 oms나 2번 구조에서 맴버변수를 추가

최종적으로 계속해서 진행할수록 해당 데이터들은 난잡해지고 변수도 너무 많이 추가된다.
따라서 여기서 자체적으로 많이 사용될것 같은 데이터들을 정리하고자 한다.

일단 의존성은 줄이기 위해 src를 사용하여
'''
import torch
import itertools
from collections import defaultdict
from codebert.embeded_parser import make_embeded_codes, tokenizer



class EmbededFunction:
    def __init__(self, src_name: str, code: str, tokens: [str] = None, tokens_ids: [int] = None, vectors: torch.tensor = None):
        self.src_name: str = src_name
        self.code = code
        self.tokens: [str] = tokens
        self.tokens_ids: [int] = tokens_ids
        self.vectors: torch.tensor = vectors

        self.cls_vec: torch.tensor = None
        self.sum_vec: torch.tensor = None
        self.avg_vec: torch.tensor = None

        self.sim_src_map = defaultdict(dict)

        #방향 벡터 유사도
        self.cos_sim_cls_vec = defaultdict(set)
        self.cos_sim_sum_vec = defaultdict(set)
        self.cos_sim_avg_vec = defaultdict(set)

        #거리 계산 유사도
        self.dist_sim_cls_vec = defaultdict(set)
        self.dist_sim_sum_vec = defaultdict(set)
        self.dist_sim_avg_vec = defaultdict(set)

        #맨허드 거리 계산 유사도 (축을 따라 이동한 거리)
        self.mdist_sim_cls_vec = defaultdict(set)
        self.mdist_sim_sum_vec = defaultdict(set)
        self.mdist_sim_avg_vec = defaultdict(set)

        self.__update_this_vectors()
        self.__update_this_tokens()


    def __str__(self):
        return self.code

    def __repr__(self):
        return self.src_name

    def get_CSA_vector(self):
        '''
        :return cls, sum, avg:
        '''
        if not self.cls_vec is None and not self.sum_vec is None and not self.avg_vec is None:
            return self.cls_vec, self.sum_vec, self.avg_vec
        else:
            self.__update_this_vectors()
            return self.cls_vec, self.sum_vec, self.avg_vec


    def __update_this_tokens(self):
        if self.tokens is None:
            self.tokens = [tokenizer.cls_token] + tokenizer.tokenize(self.code) + [tokenizer.eos_token]

        if self.tokens_ids is None:
            if self.vectors is None:
                self.tokens_ids = tokenizer.convert_tokens_to_ids(self.tokens)
            else:
                pad_num = len(self.vectors) - len(self.tokens)
                self.tokens_ids = tokenizer.convert_tokens_to_ids(self.tokens) + [tokenizer.pad_token_id for _ in range(pad_num)]


    def __update_this_vectors(self):
        if self.vectors == None:
            self.vectors, self.tokens_ids = make_embeded_codes(self.code, add_return_input_tensor=True)
            self.tokens_ids = self.tokens_ids.tolist()[0]
            self.tokens = tokenizer.convert_ids_to_tokens(self.tokens_ids)

        self.cls_vec = self.vectors[0]
        self.sum_vec = torch.sum(self.vectors, dim=0)
        self.avg_vec = torch.mean(self.vectors, dim=0)

    def clear_sim_map(self):
        self.sim_src_map = defaultdict(dict)
        
        #방향 벡터 유사도
        self.cos_sim_cls_vec = defaultdict(set)
        self.cos_sim_sum_vec = defaultdict(set)
        self.cos_sim_avg_vec = defaultdict(set)

        #거리 계산 유사도
        self.dist_sim_cls_vec = defaultdict(set)
        self.dist_sim_sum_vec = defaultdict(set)
        self.dist_sim_avg_vec = defaultdict(set)

        #맨허드 거리 계산 유사도 (축을 따라 이동한 거리)
        self.mdist_sim_cls_vec = defaultdict(set)
        self.mdist_sim_sum_vec = defaultdict(set)
        self.mdist_sim_avg_vec = defaultdict(set)
    @staticmethod
    def update_sim(embeded_funlist: ['EmbededFunction'], reset = True):
        '''
        수행 횟수 감소를 위해 동시에 업데이트. 따라서 (static으로 처리)
        :param embeded_funlist: 비교할 메서드 리스트
        :param reset: 유사도 정렬 리셋 여부
        :return:
        '''
        if reset:
            for data in embeded_funlist:
                data.clear_sim_map()
        combs = list(itertools.combinations(embeded_funlist, 2))
        for idx, (data1, data2) in enumerate(combs):
            print(f'\r{idx+1} / {len(combs)} : {data1.src_name} {data2.src_name}', end="")
            EmbededFunction.__cosine_similarity(data1, data2)
            EmbededFunction.__dist_similarity(data1, data2)
            EmbededFunction.__mdist_similarity(data1, data2)
        print()

    @staticmethod
    def __cosine_similarity(data1, data2):
        cls_vec1, sum_vec1, avg_vec1 = data1.get_CSA_vector()
        cls_vec2, sum_vec2, avg_vec2 = data2.get_CSA_vector()

        cls_cos = torch.cosine_similarity(cls_vec1, cls_vec2, dim=0)
        sum_cos = torch.cosine_similarity(sum_vec1, sum_vec2, dim=0)
        avg_cos = torch.cosine_similarity(avg_vec1, avg_vec2, dim=0)

        data1.cos_sim_cls_vec[cls_cos].add(data2)
        data2.cos_sim_cls_vec[cls_cos].add(data1)

        data1.cos_sim_sum_vec[sum_cos].add(data2)
        data2.cos_sim_sum_vec[sum_cos].add(data1)

        data1.cos_sim_avg_vec[avg_cos].add(data2)
        data2.cos_sim_avg_vec[avg_cos].add(data1)

        sim_dict = {'cls_cos' : cls_cos, 'sum_cos' : sum_cos, 'avg_cos' : avg_cos}
        data1.sim_src_map[data2.src_name] = data1.sim_src_map[data2.src_name] | sim_dict
        data2.sim_src_map[data1.src_name] = data2.sim_src_map[data1.src_name] | sim_dict


    @staticmethod
    def __dist_similarity(data1, data2):
        cls_vec1, sum_vec1, avg_vec1 = data1.get_CSA_vector()
        cls_vec2, sum_vec2, avg_vec2 = data2.get_CSA_vector()

        cls_dist = torch.dist(cls_vec1, cls_vec2, p=2)
        sum_dist = torch.dist(sum_vec1, sum_vec2, p=2)
        avg_dist = torch.dist(avg_vec1, avg_vec2, p=2)

        data1.dist_sim_cls_vec[cls_dist].add(data2)
        data2.dist_sim_cls_vec[cls_dist].add(data1)

        data1.dist_sim_sum_vec[sum_dist].add(data2)
        data2.dist_sim_sum_vec[sum_dist].add(data1)

        data1.dist_sim_avg_vec[avg_dist].add(data2)
        data2.dist_sim_avg_vec[avg_dist].add(data1)

        sim_dict = {'cls_dist' : cls_dist, 'sum_dist' : sum_dist, 'avg_dist' : avg_dist}
        data1.sim_src_map[data2.src_name] = data1.sim_src_map[data2.src_name] | sim_dict
        data2.sim_src_map[data1.src_name] = data2.sim_src_map[data1.src_name] | sim_dict

    @staticmethod
    def __mdist_similarity(data1, data2):
        cls_vec1, sum_vec1, avg_vec1 = data1.get_CSA_vector()
        cls_vec2, sum_vec2, avg_vec2 = data2.get_CSA_vector()

        cls_dist = torch.sum(torch.abs(cls_vec1-cls_vec2))
        sum_dist = torch.sum(torch.abs(sum_vec1-sum_vec2))
        avg_dist = torch.sum(torch.abs(avg_vec1-avg_vec2))

        data1.mdist_sim_cls_vec[cls_dist].add(data2)
        data2.mdist_sim_cls_vec[cls_dist].add(data1)

        data1.mdist_sim_sum_vec[sum_dist].add(data2)
        data2.mdist_sim_sum_vec[sum_dist].add(data1)

        data1.mdist_sim_avg_vec[avg_dist].add(data2)
        data2.mdist_sim_avg_vec[avg_dist].add(data1)

        sim_dict = {'cls_mdist' : cls_dist, 'sum_mdist' : sum_dist, 'avg_mdist' : avg_dist}
        data1.sim_src_map[data2.src_name] = data1.sim_src_map[data2.src_name] | sim_dict
        data2.sim_src_map[data1.src_name] = data2.sim_src_map[data1.src_name] | sim_dict




if __name__ == "__main__":
    codes = ['def print()', 'void main()', 'class Naming;', 'if Ture']
    em_list = [ EmbededFunction(src_name=code, code=code) for code in codes]
    EmbededFunction.update_sim(em_list)







        