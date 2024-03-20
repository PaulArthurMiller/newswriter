# Takes the captions from 'youtube_cap_grab' and provides them as input to
# an OpenAI model, which then writes a short news story in typical small
# town journalisic style.

from openai import OpenAI
import openai
import os
import json
import time
import logging
import youtube_cap_grab
import re

# print("Here's the first 200 chars of the prompt:")
# print(prompt[:200])

def main():
    video_id = input("Please provide the video id: ")
    prompt = youtube_cap_grab.get_transcript(video_id)
    summaries = []
    sumcount = get_summaries(prompt)
    word_count, summary = process_sumcount(sumcount)
    remaining_text = snip_prompt(word_count, prompt)
    summaries.append(summary)
    while len(remaining_text) > 100 :
        sumcount = get_summaries(remaining_text)
        word_count, summary = process_sumcount(sumcount)
        summaries.append(summary)
        remaining_text = snip_prompt(word_count, remaining_text)
    print("Summaries complete!")
    story = write_story(summaries)
    print(story)
    return story

def write_story(summaries):
    length = '400' # Story length included in model's instructions - word count
    writer_instructions = f"You are a small town newspaper journalist with over 22 years experience. You graduated near the top of your class from Ohio University's journalism school. You know Associated Press style in and out, but you have found a way to express your own voice in your stories which connects with your readers. You almost always include a humorous hook in your first few lines, where appropriate, and understand the value of the nut graf. Where a more serious tone is called for, you express empathy with the people in your news stories, which carries across to your readers. You are a stickler for facts, and never misquote or misrepresent the words of others. The veracity of the hundreds of stories you have written is your badge of honor. You get the details for your stories from summaries from meetings. You are talented at transforming these summaries into journalistic news stories for small town audiences. The story you write is optimized for search engines (SEO). Your goal is to engage the user and encourage discussion and sharing of the story. Today, you are completing a story for your Facebook news page which will be approximately {length} words and aimed at adults active in their community and its events. You always interact with users in a courteous and positive manner. You are careful to encourage diversity and inclusion in your text and are always careful to avoid stereotypes and bias."
    combined_summaries = "\n".join(summaries)
    print(combined_summaries)
    openai.api_key = os.getenv('OPENAI_API_KEY')
    if openai.api_key is not None:
        print("OpenAI API Key found!")
    else:
        print("OpenAI API Key not found. Please set it as an environment variable.")

    try:
        response = openai.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {"role": "system", "content":writer_instructions},
                {"role": "user", "content":combined_summaries},
            ],
            temperature=0.7,
            max_tokens=800,
        )
        time.sleep(1)
    except openai.RateLimitError:
        print("Rate limit exceeded. Waiting before retrying.")
        time.sleep(60)
    except openai.BadRequestError as e:
        print(f"Invalid request: {str(e)}")
    except openai.OpenAIError as e:
        print(f"An OpenAI error occurred: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

    story = response.choices[0].message.content
    return story


def get_summaries(prompt):
    digester_instructions = "You are highly skilled at sifting through video transcripts to identify subjects being discussed and the people, places, values, and other details which are important to those subjects. The transcripts you analyze are often very long, but you have a specific process you follow. Starting at the beginning of the text, you look for words and phrases which will help identify the first major subject of discussion. You remember important details such as names, groups, specific numbers like size or cost or distance, and any quotes from the individuals on the transcript which help contextualize this first subject of discussion in the transcript. When you reach a point in the transcript where the subject has changed, count the words to that point in the transcript. In your response, you will begin with the word count (in parentheses) at the point of the first subject change. You will then provide a summary of the document up to this point. The summary will include any named entities in the text and their relevance, any numeric values and their specific relevance, and any direct quotes which provide handy summations, important questions or statements of personal opinions which provide important context to the subject. The summary will be under 250 words."
    openai.api_key = os.getenv('OPENAI_API_KEY')
    if openai.api_key is not None:
        print("OpenAI API Key found!")
    else:
        print("OpenAI API Key not found. Please set it as an environment variable.")

    try:
        response = openai.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {"role": "system", "content":digester_instructions},
                {"role": "user", "content":prompt},
            ],
            temperature=0.7,
            max_tokens=600,
        )
        time.sleep(1)
    except openai.RateLimitError:
        print("Rate limit exceeded. Waiting before retrying.")
        time.sleep(60)
    except openai.BadRequestError as e:
        print(f"Invalid request: {str(e)}")
    except openai.OpenAIError as e:
        print(f"An OpenAI error occurred: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

    sumcount = response.choices[0].message.content
    print(sumcount)
    return sumcount

def process_sumcount(sumcount):
    pattern = r'^\((\d+)\)'
    match = re.search(pattern, sumcount)
    if match:
        word_count = int(match.group(1)) 
        print(f"Word count: {word_count}")
    else:
        print("Word count not found.")
    summary = re.sub(pattern + r'\s*', '', sumcount)
    print(f"Cleaned summary: {summary}")
    return word_count, summary

def snip_prompt(word_count, prompt):
    words = re.findall(r'\b\w+\b', prompt)
    remaining_words = words[word_count:]
    remaining_text = ' '.join(remaining_words)
    if remaining_text:
        print("Remaining text ready for next prompt.")
    else:
        print("Remaining text NOT ready!")
    return remaining_text
    

if __name__ == "__main__":
    main()