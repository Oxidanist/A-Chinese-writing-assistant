from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
from paddlenlp import Taskflow
import macbert
import jieba
import difflib
import re

tagger = Taskflow("pos_tagging")
p = pipeline(Tasks.text_error_correction,
             'damo/nlp_bart_text-error-correction_chinese', model_revision='v1.0.1')


def format_target_list(texts):
    target_list = [{'output': text} for text in texts]
    return target_list

# select mode




def define_pipeline(mode='default'):
    global p
    if mode == 'default':
        p = pipeline(Tasks.text_error_correction,
                     'damo/nlp_bart_text-error-correction_chinese', model_revision='v1.0.1')

    if mode == 'ernie':
        corrector = Taskflow("text_correction")

        def helper(texts):
            return format_target_list([i['target'] for i in corrector(texts)])

        p = helper
    if mode == 'macbert':
        corrector = macbert.macbert

        def helper(texts):
            return format_target_list([i for i in corrector(texts)])
        p = helper

#! model chosing
# define_pipeline(mode='default')
# define_pipeline(mode='macbert')
# define_pipeline(mode='erine')




def chinese_word_segmentation(text, cut_all_mode=1):
    seg_list = jieba.cut(text, cut_all=cut_all_mode)
    return " ".join(seg_list)


def smallest_word(s_ls, t_ls):
    for i in range(len(t_ls)):
        for j in range(len(t_ls)):
            if i == len(t_ls) or j == len(t_ls):
                break
            if i != j:
                if t_ls[i] in t_ls[j]:
                    t_ls.pop(j)

    for i in range(len(s_ls)):
        for j in range(len(s_ls)):
            if i == len(s_ls) or j == len(s_ls):
                break
            if i != j:
                if s_ls[i] in s_ls[j]:
                    s_ls.pop(j)
    return s_ls, t_ls


def get_changes(source, target):
    a = chinese_word_segmentation(source)
    b = chinese_word_segmentation(target)

    s_ls = [i for i in a.split() if i not in b.split()]
    t_ls = [i for i in b.split() if i not in a.split()]
    return smallest_word(s_ls, t_ls)


def get_changed_word_in_sentence(sentence, char_pos):
    seg = chinese_word_segmentation(sentence, 0)
    count = 0
    for i in seg.split():
        count += len(i)
        if count > char_pos:
            return i
# and type


def get_changes_difflib(a, b, mode='char'):
    diff = difflib.SequenceMatcher(None, a, b)
    opcodes = diff.get_opcodes()
    changes = []
    if mode == 'char':
        for tag, i1, i2, j1, j2 in opcodes:
            if tag == 'equal':
                continue
            elif tag == 'delete':
                changes.append(('-', tagger(f'{a[i1:i2]}')))
            elif tag == 'insert':
                changes.append(('+', tagger(f'{b[j1:j2]}')))
            else:
                changes.append(
                    (tagger(f'{a[i1:i2]}'), '->', tagger(f'{b[j1:j2]}')))
    else:
        for tag, i1, i2, j1, j2 in opcodes:
            if tag == 'equal':
                continue
            elif tag == 'delete':
                changes.append(
                    ('-', tagger(f'{get_changed_word_in_sentence(a,i1)}')))
            elif tag == 'insert':
                changes.append(
                    ('+', tagger(f'{get_changed_word_in_sentence(b,j1)}')))
            else:
                changes.append((tagger(f'{get_changed_word_in_sentence(a,i1)}'),
                               '->', tagger(f'{get_changed_word_in_sentence(b,j1)}')))
    return changes


def res_formatted(origin, results, mode='char'):  # input: origin text and target text
    new_res = []

    for i in range(len(origin)):

        new_res.append({'source': origin[i], 'target': results[i]['output']})

    for i in new_res:
        if i['source'] == i['target']:
            i['changes'] = ''
        else:
            i['changes'] = get_changes_difflib(i['source'], i['target'], mode)

    return new_res


def split_sentences(text):
    return re.split(r'(?<=[？?！!。；;])', text)


def get_output(inputs):
    tag_meaning = {
        'n': 'common noun',
        'f': 'locative noun',
        's': 'place noun',
        't': 'time noun',
        'nr': 'person name',
        'ns': 'place name',
        'nt': 'organization name',
        'nw': 'work name',
        'nz': 'other proper noun',
        'v': 'verb',
        'vd': 'verb adverbial',
        'vn': 'verb noun',
        'a': 'adjective',
        'ad': 'adverbial adjective',
        'an': 'adjectival noun',
        'd': 'adverb',
        'm': 'numeral',
        'q': 'quantifier',
        'r': 'pronoun',
        'p': 'preposition',
        'c': 'conjunction',
        'u': 'auxiliary',
        'xc': 'function words',
        'w': 'punctuation',
        'PER': 'person name',
        'LOC': 'place name',
        'ORG': 'organization name',
        'TIME': 'time'
    }
    sentences = split_sentences(inputs)
    for i in sentences:
        if i == '':
            sentences.remove(i)
    formatted = res_formatted(sentences, p(sentences), mode='word')
    outputstring = ''
    for i in formatted:
        outputstring += 'do you mean: ' + i['target']+'\n'
        for j in i['changes']:
            if '-' in j:
                outputstring += 'deleted ' + \
                    j[-1][0][0] + '(%s)' % tag_meaning[j[-1][0][1]]+'\n'
            if '+' in j:
                outputstring += 'adding ' + \
                    j[-1][0][0] + '(%s)' % tag_meaning[j[-1][0][1]] + '\n'
            if '->' in j:
                split_index = j.index("->")
                before = j[:split_index]
                after = j[split_index+1:]
                outputstring += 'changed ' + \
                    before[0][0][0] + '(%s)' % tag_meaning[before[0][0][1]]
                outputstring += 'to '+after[0][0][0] + \
                    '(%s)' % tag_meaning[before[0][0][1]]+'\n'
    return outputstring




def get_target_list(sentences):
    return [i['target'] for i in res_formatted(sentences, p(sentences), mode='word')]

def get_res_formatted(sentences,mode='word'):
    return res_formatted(sentences, p(sentences),mode)


