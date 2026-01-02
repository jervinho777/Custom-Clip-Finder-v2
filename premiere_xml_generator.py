#!/usr/bin/env python3
"""
PREMIERE PRO XML GENERATOR v3
Based on ACTUAL working Premiere Pro XML export.
"""

import json
import subprocess
import uuid
from pathlib import Path

PPRO_TICKS_PER_SECOND = 254016000000

def get_video_info(video_path):
    cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', str(video_path)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        video_stream = next((s for s in data.get('streams', []) if s.get('codec_type') == 'video'), None)
        audio_stream = next((s for s in data.get('streams', []) if s.get('codec_type') == 'audio'), None)
        duration = float(data.get('format', {}).get('duration', 600))
        fps = 25
        if video_stream:
            fps_str = video_stream.get('r_frame_rate', '25/1')
            if '/' in fps_str:
                num, den = map(int, fps_str.split('/'))
                fps = round(num / den) if den > 0 else 25
        return {
            'duration': duration, 'duration_frames': int(duration * fps), 'fps': fps,
            'width': video_stream.get('width', 1920) if video_stream else 1920,
            'height': video_stream.get('height', 1080) if video_stream else 1080,
            'sample_rate': int(audio_stream.get('sample_rate', 48000)) if audio_stream else 48000,
            'path': str(Path(video_path).absolute()), 'filename': Path(video_path).name
        }
    except:
        return {'duration': 600, 'duration_frames': 15000, 'fps': 25, 'width': 1920, 'height': 1080,
                'sample_rate': 48000, 'path': str(Path(video_path).absolute()), 'filename': Path(video_path).name}

def generate_premiere_xml(segments, source_video_path, output_path, sequence_name="Clip"):
    vi = get_video_info(source_video_path)
    fps, width, height = vi['fps'], vi['width'], vi['height']
    sample_rate, source_dur = vi['sample_rate'], vi['duration_frames']
    pathurl = "file://localhost" + vi['path'].replace(" ", "%20")
    
    total_dur = sum(int((s.get('end', 0) - s.get('start', 0)) * fps) for s in segments)
    seq_uuid = str(uuid.uuid4())
    
    v_clips, a1_clips, a2_clips = "", "", ""
    tpos = 0
    
    for i, seg in enumerate(segments):
        in_f = int(seg.get('start', 0) * fps)
        out_f = int(seg.get('end', seg.get('start', 0) + 5) * fps)
        dur_f = out_f - in_f
        t_start, t_end = tpos, tpos + dur_f
        ticks_in = int(seg.get('start', 0) * PPRO_TICKS_PER_SECOND)
        ticks_out = int(seg.get('end', 0) * PPRO_TICKS_PER_SECOND)
        cid_v, cid_a1, cid_a2 = 100+i, 200+i, 300+i
        
        v_clips += f'''
				<clipitem id="clipitem-{cid_v}">
					<masterclipid>masterclip-1</masterclipid>
					<n>{vi['filename']}</n>
					<enabled>TRUE</enabled>
					<duration>{source_dur}</duration>
					<rate><timebase>{fps}</timebase><ntsc>FALSE</ntsc></rate>
					<start>{t_start}</start>
					<end>{t_end}</end>
					<in>{in_f}</in>
					<out>{out_f}</out>
					<pproTicksIn>{ticks_in}</pproTicksIn>
					<pproTicksOut>{ticks_out}</pproTicksOut>
					<alphatype>none</alphatype>
					<pixelaspectratio>square</pixelaspectratio>
					<anamorphic>FALSE</anamorphic>
					<file id="file-1"/>
					<link><linkclipref>clipitem-{cid_v}</linkclipref><mediatype>video</mediatype><trackindex>1</trackindex><clipindex>{i+1}</clipindex></link>
					<link><linkclipref>clipitem-{cid_a1}</linkclipref><mediatype>audio</mediatype><trackindex>1</trackindex><clipindex>{i+1}</clipindex><groupindex>1</groupindex></link>
					<link><linkclipref>clipitem-{cid_a2}</linkclipref><mediatype>audio</mediatype><trackindex>2</trackindex><clipindex>{i+1}</clipindex><groupindex>1</groupindex></link>
				</clipitem>'''
        
        a1_clips += f'''
				<clipitem id="clipitem-{cid_a1}" premiereChannelType="stereo">
					<masterclipid>masterclip-1</masterclipid>
					<n>{vi['filename']}</n>
					<enabled>TRUE</enabled>
					<duration>{source_dur}</duration>
					<rate><timebase>{fps}</timebase><ntsc>FALSE</ntsc></rate>
					<start>{t_start}</start>
					<end>{t_end}</end>
					<in>{in_f}</in>
					<out>{out_f}</out>
					<pproTicksIn>{ticks_in}</pproTicksIn>
					<pproTicksOut>{ticks_out}</pproTicksOut>
					<file id="file-1"/>
					<sourcetrack><mediatype>audio</mediatype><trackindex>1</trackindex></sourcetrack>
					<link><linkclipref>clipitem-{cid_v}</linkclipref><mediatype>video</mediatype><trackindex>1</trackindex><clipindex>{i+1}</clipindex></link>
					<link><linkclipref>clipitem-{cid_a1}</linkclipref><mediatype>audio</mediatype><trackindex>1</trackindex><clipindex>{i+1}</clipindex><groupindex>1</groupindex></link>
					<link><linkclipref>clipitem-{cid_a2}</linkclipref><mediatype>audio</mediatype><trackindex>2</trackindex><clipindex>{i+1}</clipindex><groupindex>1</groupindex></link>
				</clipitem>'''
        
        a2_clips += f'''
				<clipitem id="clipitem-{cid_a2}" premiereChannelType="stereo">
					<masterclipid>masterclip-1</masterclipid>
					<n>{vi['filename']}</n>
					<enabled>TRUE</enabled>
					<duration>{source_dur}</duration>
					<rate><timebase>{fps}</timebase><ntsc>FALSE</ntsc></rate>
					<start>{t_start}</start>
					<end>{t_end}</end>
					<in>{in_f}</in>
					<out>{out_f}</out>
					<pproTicksIn>{ticks_in}</pproTicksIn>
					<pproTicksOut>{ticks_out}</pproTicksOut>
					<file id="file-1"/>
					<sourcetrack><mediatype>audio</mediatype><trackindex>2</trackindex></sourcetrack>
					<link><linkclipref>clipitem-{cid_v}</linkclipref><mediatype>video</mediatype><trackindex>1</trackindex><clipindex>{i+1}</clipindex></link>
					<link><linkclipref>clipitem-{cid_a1}</linkclipref><mediatype>audio</mediatype><trackindex>1</trackindex><clipindex>{i+1}</clipindex><groupindex>1</groupindex></link>
					<link><linkclipref>clipitem-{cid_a2}</linkclipref><mediatype>audio</mediatype><trackindex>2</trackindex><clipindex>{i+1}</clipindex><groupindex>1</groupindex></link>
				</clipitem>'''
        tpos = t_end
    
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xmeml>
<xmeml version="4">
	<sequence id="sequence-1">
		<uuid>{seq_uuid}</uuid>
		<duration>{total_dur}</duration>
		<rate><timebase>{fps}</timebase><ntsc>FALSE</ntsc></rate>
		<n>{sequence_name}</n>
		<media>
			<video>
				<format>
					<samplecharacteristics>
						<rate><timebase>{fps}</timebase><ntsc>FALSE</ntsc></rate>
						<width>{width}</width>
						<height>{height}</height>
						<anamorphic>FALSE</anamorphic>
						<pixelaspectratio>square</pixelaspectratio>
						<fielddominance>none</fielddominance>
						<colordepth>24</colordepth>
					</samplecharacteristics>
				</format>
				<track>{v_clips}
					<enabled>TRUE</enabled>
					<locked>FALSE</locked>
				</track>
			</video>
			<audio>
				<format>
					<samplecharacteristics>
						<depth>16</depth>
						<samplerate>{sample_rate}</samplerate>
					</samplecharacteristics>
				</format>
				<track premiereTrackType="Stereo">{a1_clips}
					<enabled>TRUE</enabled>
					<locked>FALSE</locked>
					<outputchannelindex>1</outputchannelindex>
				</track>
				<track premiereTrackType="Stereo">{a2_clips}
					<enabled>TRUE</enabled>
					<locked>FALSE</locked>
					<outputchannelindex>2</outputchannelindex>
				</track>
			</audio>
		</media>
		<timecode>
			<rate><timebase>{fps}</timebase><ntsc>FALSE</ntsc></rate>
			<string>00:00:00:00</string>
			<frame>0</frame>
			<displayformat>NDF</displayformat>
		</timecode>
	</sequence>
	<clip id="masterclip-1">
		<n>{vi['filename']}</n>
		<duration>{source_dur}</duration>
		<rate><timebase>{fps}</timebase><ntsc>FALSE</ntsc></rate>
		<file id="file-1">
			<n>{vi['filename']}</n>
			<pathurl>{pathurl}</pathurl>
			<rate><timebase>{fps}</timebase><ntsc>FALSE</ntsc></rate>
			<duration>{source_dur}</duration>
			<timecode>
				<rate><timebase>{fps}</timebase><ntsc>FALSE</ntsc></rate>
				<string>00:00:00:00</string>
				<frame>0</frame>
				<displayformat>NDF</displayformat>
			</timecode>
			<media>
				<video>
					<samplecharacteristics>
						<rate><timebase>{fps}</timebase><ntsc>FALSE</ntsc></rate>
						<width>{width}</width>
						<height>{height}</height>
						<anamorphic>FALSE</anamorphic>
						<pixelaspectratio>square</pixelaspectratio>
						<fielddominance>none</fielddominance>
					</samplecharacteristics>
				</video>
				<audio>
					<samplecharacteristics>
						<depth>16</depth>
						<samplerate>{sample_rate}</samplerate>
					</samplecharacteristics>
					<channelcount>2</channelcount>
				</audio>
			</media>
		</file>
	</clip>
</xmeml>'''
    
    with open(output_path, 'w', encoding='utf-8-sig') as f:
        f.write(xml)
    print(f"Generated: {output_path} ({len(segments)} segments, {total_dur/fps:.1f}s)")
    return output_path

def generate_from_clip_info(info_json_path, source_video_path):
    with open(info_json_path, 'r') as f:
        data = json.load(f)
    segments = data.get('structure', {}).get('segments', [])
    if not segments:
        print(f"No segments in {info_json_path}")
        return None
    output_path = Path(info_json_path).with_suffix('.xml')
    return generate_premiere_xml(segments, source_video_path, output_path, data.get('version_id', 'Clip'))

if __name__ == "__main__":
    import sys
    print("PREMIERE PRO XML GENERATOR v3")
    if len(sys.argv) >= 3:
        generate_from_clip_info(sys.argv[1], sys.argv[2])
    else:
        print("\nUsage: python premiere_xml_generator.py <info.json> <video.mp4>")
        if input("\nTest? (y/n): ").lower() == 'y':
            video = input("Video path: ").strip()
            if video and Path(video).exists():
                test_segs = [
                    {'role': 'hook', 'start': 120.0, 'end': 126.0},
                    {'role': 'context', 'start': 110.0, 'end': 120.0},
                    {'role': 'content', 'start': 126.0, 'end': 155.0},
                    {'role': 'payoff', 'start': 155.0, 'end': 165.0}
                ]
                generate_premiere_xml(test_segs, video, Path(video).parent / "test_sequence.xml", "Test_Clip")
