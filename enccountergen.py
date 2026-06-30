import os
from datetime import datetime
from PIL import Image

def generate_custom_counter():
    # Prompt the user for the file path directly in the console
    image_path = input("Enter the path to your GIF or image file: ").strip()
    
    # Strip quotes if the user dragged and dropped the file into the terminal
    image_path = image_path.strip("'\"")

    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' not found. Please check the path and try again.")
        return

    output_root = "output"

    # Extract naming details
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    animation_folder_name = f"{base_name}_{timestamp}"
    
    # Define paths
    animation_root_dir = os.path.join(output_root, animation_folder_name)
    data_dir = os.path.join(animation_root_dir, "data")
    anim_dir = os.path.join(data_dir, "anim")
    os.makedirs(anim_dir, exist_ok=True)

    # Open image and extract frames
    with Image.open(image_path) as img:
        frames_data = []
        frame_idx = 0
        
        # Save the very first frame as icon.png in the animation root directory
        icon_path = os.path.join(animation_root_dir, "icon.png")
        img.seek(0)
        icon_img = img.convert("RGB")
        icon_img.save(icon_path, "PNG")
        
        while True:
            # Determine duration (default to 100ms if not specified)
            duration = img.info.get("duration", 100)
            if duration == 0:
                duration = 100
            
            # Format filename matching your structure
            delay_sec = duration / 1000.0
            frame_filename = f"frame_{frame_idx:02d}_delay-{delay_sec:.1f}s.jpg"
            frame_filepath = os.path.join(anim_dir, frame_filename)
            
            # Convert to RGB and save as JPG
            rgb_img = img.convert("RGB")
            rgb_img.save(frame_filepath, "JPEG")
            
            # Store metadata for XML generation
            area_name = f"bg-f{frame_idx+1:05d}"
            frames_data.append({
                "file": f"anim/{frame_filename}",
                "area_name": area_name,
                "duration": duration
            })
            
            frame_idx += 1
            try:
                img.seek(frame_idx)
            except EOFError:
                break # End of GIF frames

    # --- Generate custom-counter.xml Content ---
    custom_counter_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '',
        '<themes>'
    ]
    
    for f in frames_data:
        custom_counter_lines.append(f'<images file="{f["file"]}" filter="nearest">')
        custom_counter_lines.append(f'    <area name="{f["area_name"]}" xywh="*"/>')
        custom_counter_lines.append('</images>')
        custom_counter_lines.append('')
        
    custom_counter_lines.append('    <images>')
    custom_counter_lines.append('        <animation name="encounter_counter_anim" timeSource="enabled">')
    for f in frames_data:
        custom_counter_lines.append(f'  <frame ref="{f["area_name"]}" duration="{f["duration"]}"/>')
    custom_counter_lines.append('        </animation>')
    custom_counter_lines.append('    </images>')
    custom_counter_lines.append('    ')
    
    custom_counter_lines.append("""  <theme name="encounter-counter" ref="resizableframe">
    <param name="titleAreaTop"><int>8</int></param>
    <param name="titleAreaLeft"><int>11</int></param>
    <param name="titleAreaRight"><int>-1</int></param>
    <param name="titleAreaBottom"><int>20</int></param>
    <param name="border"><border>20,0,0,0</border></param>
    <param name="background"><image>encounter_counter_anim</image></param>
    <param name="minWidth"><int>200</int></param>
    <theme name="content" ref="-defaults">
      <theme name="label" ref="label">
        <param name="minWidth"><int>50</int></param>
        <param name="font"><font>alphabeta-border</font></param>
        <param name="border"><border>7,7</border></param>
        <param name="textAlignment"><enum type="alignment">CENTER</enum></param>
      </theme>
      <theme name="label-left" ref="label">
        <param name="textAlignment"><enum type="alignment">LEFT</enum></param>
      </theme>
      <theme name="icon" ref="label">
        <param name="border"><border>7,7</border></param>
      </theme>
      <theme name="cell" ref="label">
        <param name="background"><image>ui-inputbox.background</image></param>
        <param name="textAlignment"><enum type="alignment">LEFT</enum></param>
        <param name="border"><border>5</border></param>
      </theme>
    </theme>
  </theme>

   <theme name="encounter-counter-expanded" ref="encounter-counter">
      <param name="background"><image>encounter_counter_anim</image></param>
 </theme>

</themes>""")

    # Write out data/custom-counter.xml
    custom_counter_path = os.path.join(data_dir, "custom-counter.xml")
    with open(custom_counter_path, "w", encoding="utf-8") as xml_file:
        xml_file.write("\n".join(custom_counter_lines))

    # --- Generate info.xml Content ---
    info_xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<resource name="{base_name}" version="1.0" description="Custom encounter counter - created with enccountergen" author="enccountergen" weblink="https://github.com/cassnadra?tab=repositories">
  <theme_extensions theme_extension_revision="1">
    <theme_extension name="{base_name}" path="data/custom-counter.xml" is_mobile="false"/>
  </theme_extensions>
</resource>"""

    # Write out info.xml to the root of the animation folder
    info_xml_path = os.path.join(animation_root_dir, "info.xml")
    with open(info_xml_path, "w", encoding="utf-8") as xml_file:
        xml_file.write(info_xml_content)

    print("\n--- Processing Complete ---")
    print(f"Processed {frame_idx} frames successfully.")
    print(f"Directory Created: {animation_root_dir}/")
    print(f"├── icon.png")
    print(f"├── info.xml")
    print(f"└── data/")
    print(f"    ├── custom-counter.xml")
    print(f"    └── anim/ (Contains {frame_idx} extracted frames)")

if __name__ == "__main__":
    generate_custom_counter()