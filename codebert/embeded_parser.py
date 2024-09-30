from transformers import AutoTokenizer, AutoModel
import torch
import gc

# 모델이 None인 경우에만 실행되도록 설정
if 'model' not in globals():
    tokenizer = AutoTokenizer.from_pretrained("microsoft/longcoder-base")
    model = AutoModel.from_pretrained("microsoft/LongCoder-base")
    nl_tokens = tokenizer.tokenize("return maximum value")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("model set :", device)
    model.to(device)
    model.eval()

def tokenize_codes(codes: str):
    '''
    str, ids 두개로 분리하여 토큰화된 데이터를 반환. (ids에는 패딩 적용)
    '''
    tokens_list = []
    ids_list = []
    attentions_list = []

    if isinstance(codes, str):
        codes = [codes]

    max_length = 0
    for code in codes:
        tokens = [tokenizer.cls_token] + tokenizer.tokenize(code) + [tokenizer.eos_token]
        tokens_ids = tokenizer.convert_tokens_to_ids(tokens)
        attentions_list.append([1 for _ in range(len(tokens))])
        tokens_list.append(tokens)
        ids_list.append(tokens_ids)

        if max_length < len(tokens):
            max_length = len(tokens)

    for idx in range(len(ids_list)):
        idx_size = len(ids_list[idx])
        ids_list[idx] = ids_list[idx] + [tokenizer.pad_token_id for _ in range(max_length - idx_size)]

    return ids_list




def make_embeded_codes(codes: torch.tensor, add_return_input_tensor=False, print_progress = False):
    '''
    str, [str], [int]: 토큰화 되었다고 가정, tensor 입력하면 임베딩 텐서를 반환
    :param codes: 소스코드, 소스코드 리스트, 토큰화된 리스트, 입력 직전 텐서
    :param add_return_input_tensor: 입력 직전 텐서 추가 반환 여부
    :return: 임베딩된 벡터 + (입력 텐서)
    '''
    ids_tensor = codes
    if isinstance(codes, str):
        codes = [codes]

    if isinstance(codes[0], str):
        codes = tokenize_codes(codes)

    if isinstance(codes[0], list):
        ids_tensor = torch.tensor(codes)
    elif isinstance(codes, torch.tensor):
        ids_tensor = codes

    if print_progress:
        print("ip: ", ids_tensor.shape)

    result = []
    input_size = len(ids_tensor)
    batch_size = 10
    batch_count = int(input_size/batch_size + 0.9)
    attention_mask = (ids_tensor != tokenizer.pad_token_id).int()

    for c in range(batch_count):
        st_idx = batch_size * c
        ed_idx = batch_size * (c + 1)
        if input_size < ed_idx:
            ed_idx = input_size

        cuda_at = attention_mask[st_idx:ed_idx].to(device)

        cuda_ids = ids_tensor[st_idx:ed_idx].to(device)
        with torch.no_grad():
            cuda_result = model(cuda_ids, cuda_at)

        cpu_result = cuda_result[0].cpu()  #
        result.append(cpu_result)

        del cuda_ids, cuda_result, cuda_at
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
        gc.collect()

        if print_progress:
            print(f"\rprogress {c+1}/{batch_count} : {ed_idx-st_idx}", end=" ")

    if print_progress:
        print("done")

    if add_return_input_tensor:
        return torch.cat(result, dim=0), ids_tensor
    else:
        return torch.cat(result, dim=0)

if __name__ == "__main__":
    print(tokenizer.vocab_size)
    size = 25
    temp_datas = []
    for i in range(size-2):
        temp_datas.append([tokenizer.cls_token_id] + [j+10 for j in range(i)] + [tokenizer.eos_token_id])
        pads = [tokenizer.pad_token_id for _ in range(size - len(temp_datas[i]))]

        temp_datas[i] = temp_datas[i] + pads
    tks = make_embeded_codes(temp_datas, print_progress=True)
    print(tks.shape)



#
# # embeded code test
# codes = []
# num = 0
# for key, pair in ap_cad_cronw_same_map.items():
#     # print(f'\r{key} {num}/{len(ap_cad_cronw_same_map)}', end="")
#     for i in range(2):
#         codes.append(pair[i].code)
#
#         reuslt = make_embeded_codes(codes)