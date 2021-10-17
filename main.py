import praw
from urllib.request import urlretrieve
import moviepy.editor as mp
import random
import string
import copyright
import glob
import json
import os

with open('params.json') as f:
    params = json.load(f)
royalty_free = glob.glob("royaltyfree/*")


def fetch_videos():
    reddit = praw.Reddit(client_id=params['client_id'], client_secret=params['client_secret'],
                         user_agent=params['user_agent'])
    return reddit.subreddit(params['subreddit']).top(limit=params['videos_to_fetch'], time_filter=params['time_span'])


def organize_file_download(posts):
    media_list = []
    for post in posts:
        print(post.url)
        if post.is_video and params['nsfw'] == post.over_18:
            file_name = ''.join(random.choice(string.ascii_letters) for x in range(10))
            download_path = os.path.join('downloads/', file_name + '_video.mp4')
            try:
                video = urlretrieve(post.media['reddit_video']['fallback_url'], download_path)[0]
                audio = get_audio(post, file_name)
                media_list.append([video, audio])
            except Exception as e:
                print('Could not download video or audio, ignoring... ' + str(e))
                pass
    print(media_list)
    return media_list


def get_audio(post, file_name):
    download_path = os.path.join('downloads/', file_name + '_audio.mp4')
    try:
        audio = urlretrieve(str(post.url) + '/DASH_audio.mp4?', download_path)[0]
    except Exception:
        try:
            audio = urlretrieve(str(post.url) + '/audio', download_path)[0]
        except Exception:
            if params['add_royalty_music']:
                return royalty_free[random.randint(0, len(royalty_free) - 1)]
            else:
                return None
    if params['replace_copyrighted_audio']:
        if copyright.check_video(audio):
            return audio
        else:
            if params['add_royalty_music']:
                return royalty_free[random.randint(0, len(royalty_free) - 1)]
            return None
    return audio


def compile_clips(media):
    total_length = 0
    final_clips = []
    for video in media:
        if params['ignore_videos_without_sound'] and video[1] is None:
            continue
        if total_length > 600:
            break
        clip = mp.VideoFileClip(video[0])
        if not params['merge_resolutions']:
            clip = clip.resize((params['resolution'][0], params['resolution'][1]))
        audio = mp.AudioFileClip(video[1])
        if params['add_royalty_music']:
            audio = audio.set_duration(clip.duration)  # maybe set this duration only if royalty
        clip = clip.set_audio(audio)
        total_length += clip.duration
        final_clips.append(clip)
    final = mp.concatenate_videoclips(final_clips, method='compose')
    final.write_videofile('final.mp4')


compile_clips(organize_file_download(fetch_videos()))
