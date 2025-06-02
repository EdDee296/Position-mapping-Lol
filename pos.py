import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as patches
import numpy as np

# --- CONFIGURATION ---
MINIMAP_IMAGE_PATH = "C:/Users/ASUS/OneDrive/New folder/a.png"  # Use your path

# Mid Lane (Diagonal: y = 1-x + offset_y)
INITIAL_MID_THRESHOLD = 0.05
INITIAL_MID_OFFSET_Y = 0.05

# Top Lane Horizontal (Line: y = offset_y)
INITIAL_TOP_Y_OFFSET = 0.13
INITIAL_TOP_Y_THRESHOLD = 0.03

# Top Lane Vertical (Line: x = offset_x)
INITIAL_TOP_X_OFFSET = 0.13
INITIAL_TOP_X_THRESHOLD = 0.03

# Bot Lane Horizontal (Line: y = offset_y, near bottom)
INITIAL_BOT_Y_OFFSET = 0.905  # Center of horizontal band from the top (closer to 1.0 for bottom)
INITIAL_BOT_Y_THRESHOLD = 0.03

# Bot Lane Vertical (Line: x = offset_x, near right)
INITIAL_BOT_X_OFFSET = 0.905  # Center of vertical band from the left (closer to 1.0 for right)
INITIAL_BOT_X_THRESHOLD = 0.03

BASE_RADIUS = 0.4

# --- GLOBAL VARIABLES FOR SHARED ACCESS ---
minimap_width = 0
minimap_height = 0
fig = None
ax = None

# Mid Lane variables
current_mid_threshold = INITIAL_MID_THRESHOLD
current_mid_offset_y = INITIAL_MID_OFFSET_Y
mid_band_patch, mid_center_line, mid_upper_line, mid_lower_line = None, None, None, None

# Top Lane Horizontal variables
current_top_y_offset = INITIAL_TOP_Y_OFFSET
current_top_y_threshold = INITIAL_TOP_Y_THRESHOLD
top_y_band_patch, top_y_center_line, top_y_upper_line, top_y_lower_line = None, None, None, None

# Top Lane Vertical variables
current_top_x_offset = INITIAL_TOP_X_OFFSET
current_top_x_threshold = INITIAL_TOP_X_THRESHOLD
top_x_band_patch, top_x_center_line, top_x_right_line, top_x_left_line = None, None, None, None

# Bot Lane Horizontal variables
current_bot_y_offset = INITIAL_BOT_Y_OFFSET
current_bot_y_threshold = INITIAL_BOT_Y_THRESHOLD
bot_y_band_patch, bot_y_center_line, bot_y_upper_line, bot_y_lower_line = None, None, None, None

# Bot Lane Vertical variables
current_bot_x_offset = INITIAL_BOT_X_OFFSET
current_bot_x_threshold = INITIAL_BOT_X_THRESHOLD
bot_x_band_patch, bot_x_center_line, bot_x_right_line, bot_x_left_line = None, None, None, None


# --- FUNCTIONS ---
def clear_artist(artist):
    """Safely remove a matplotlib artist (patch or line)."""
    if artist:
        if isinstance(artist, list) and artist:
            if artist[0] in ax.lines: artist.pop(0).remove()
        elif artist in ax.patches:
            artist.remove()
    return None

def onclick(event):
    global minimap_width, minimap_height
    global current_mid_threshold, current_mid_offset_y
    global current_top_y_offset, current_top_y_threshold
    global current_top_x_offset, current_top_x_threshold
    global current_bot_y_offset, current_bot_y_threshold
    global current_bot_x_offset, current_bot_x_threshold

    if event.inaxes == ax and event.xdata is not None and event.ydata is not None:
        pixel_x = int(round(event.xdata))
        pixel_y = int(round(event.ydata))
        pixel_x = max(0, min(pixel_x, minimap_width - 1))
        pixel_y = max(0, min(pixel_y, minimap_height - 1))
        norm_x = pixel_x / minimap_width
        norm_y = pixel_y / minimap_height
        
        mid_center_y_val = (1 - norm_x) + current_mid_offset_y
        is_in_mid = (mid_center_y_val - current_mid_threshold <= norm_y <= 
                     mid_center_y_val + current_mid_threshold)

        is_in_top_y = (current_top_y_offset - current_top_y_threshold <= norm_y <=
                       current_top_y_offset + current_top_y_threshold)
        is_in_top_x = (current_top_x_offset - current_top_x_threshold <= norm_x <=
                       current_top_x_offset + current_top_x_threshold)

        is_in_bot_y = (current_bot_y_offset - current_bot_y_threshold <= norm_y <=
                       current_bot_y_offset + current_bot_y_threshold)
        is_in_bot_x = (current_bot_x_offset - current_bot_x_threshold <= norm_x <=
                       current_bot_x_offset + current_bot_x_threshold)

        dist_left_base = np.sqrt((norm_x - 0)**2 + (norm_y - 1)**2)
        dist_right_base = np.sqrt((norm_x - 1)**2 + (norm_y - 0)**2)
        
        location_found = False
        if dist_left_base <= BASE_RADIUS:
            print("Left Base")
            location_found = True
        elif dist_right_base <= BASE_RADIUS:
            print("Right Base")
            location_found = True
        else:
            if is_in_mid:
                print("Mid Lane")
                location_found = True
            elif is_in_top_y or is_in_top_x: 
                print("Top Lane")
                location_found = True
            elif is_in_bot_y or is_in_bot_x:
                print("Bot Lane")
                location_found = True
        
        if not location_found:
            print(
                f"Clicked: Pixel (x={pixel_x}, y={pixel_y}) | Normalized (nx={norm_x:.3f}, ny={norm_y:.3f})")

def update_visuals():
    global mid_band_patch, mid_center_line, mid_upper_line, mid_lower_line
    global top_y_band_patch, top_y_center_line, top_y_upper_line, top_y_lower_line
    global top_x_band_patch, top_x_center_line, top_x_right_line, top_x_left_line
    global bot_y_band_patch, bot_y_center_line, bot_y_upper_line, bot_y_lower_line
    global bot_x_band_patch, bot_x_center_line, bot_x_right_line, bot_x_left_line
    global minimap_width, minimap_height, ax, fig
    global current_mid_threshold, current_mid_offset_y
    global current_top_y_offset, current_top_y_threshold, current_top_x_offset, current_top_x_threshold
    global current_bot_y_offset, current_bot_y_threshold, current_bot_x_offset, current_bot_x_threshold

    # --- Clear previous artists ---
    artists_to_clear = [
        mid_band_patch, mid_center_line, mid_upper_line, mid_lower_line,
        top_y_band_patch, top_y_center_line, top_y_upper_line, top_y_lower_line,
        top_x_band_patch, top_x_center_line, top_x_right_line, top_x_left_line,
        bot_y_band_patch, bot_y_center_line, bot_y_upper_line, bot_y_lower_line,
        bot_x_band_patch, bot_x_center_line, bot_x_right_line, bot_x_left_line
    ]
    cleared_artists = [clear_artist(art) for art in artists_to_clear]
    (mid_band_patch, mid_center_line, mid_upper_line, mid_lower_line,
     top_y_band_patch, top_y_center_line, top_y_upper_line, top_y_lower_line,
     top_x_band_patch, top_x_center_line, top_x_right_line, top_x_left_line,
     bot_y_band_patch, bot_y_center_line, bot_y_upper_line, bot_y_lower_line,
     bot_x_band_patch, bot_x_center_line, bot_x_right_line, bot_x_left_line) = cleared_artists


    # --- Draw Mid Lane Band ---
    mid_verts_pixel = [
        (0 * minimap_width, ((1 - 0 + current_mid_offset_y) - current_mid_threshold) * minimap_height),
        (1 * minimap_width, ((1 - 1 + current_mid_offset_y) - current_mid_threshold) * minimap_height),
        (1 * minimap_width, ((1 - 1 + current_mid_offset_y) + current_mid_threshold) * minimap_height),
        (0 * minimap_width, ((1 - 0 + current_mid_offset_y) + current_mid_threshold) * minimap_height),
    ]
    mid_band_patch = ax.add_patch(patches.Polygon(mid_verts_pixel, closed=True, edgecolor='none', facecolor='cyan', alpha=0.3, zorder=2))
    norm_x_coords_mid = np.array([0, 1])
    center_x_pixel_mid = norm_x_coords_mid * minimap_width
    mid_center_y_pixel = (1 - norm_x_coords_mid + current_mid_offset_y) * minimap_height
    mid_center_line = ax.plot(center_x_pixel_mid, mid_center_y_pixel, 'm--', lw=1, label='Mid Center', zorder=3)
    mid_upper_line = ax.plot(center_x_pixel_mid, ((1 - norm_x_coords_mid + current_mid_offset_y) + current_mid_threshold) * minimap_height, 'm-', lw=0.8, alpha=0.7, zorder=3)
    mid_lower_line = ax.plot(center_x_pixel_mid, ((1 - norm_x_coords_mid + current_mid_offset_y) - current_mid_threshold) * minimap_height, 'm-', lw=0.8, alpha=0.7, zorder=3)

    # --- Draw Top Lane Horizontal Band ---
    top_y_verts_pixel = [
        (0 * minimap_width, (current_top_y_offset - current_top_y_threshold) * minimap_height),
        (1 * minimap_width, (current_top_y_offset - current_top_y_threshold) * minimap_height),
        (1 * minimap_width, (current_top_y_offset + current_top_y_threshold) * minimap_height),
        (0 * minimap_width, (current_top_y_offset + current_top_y_threshold) * minimap_height),
    ]
    top_y_band_patch = ax.add_patch(patches.Polygon(top_y_verts_pixel, closed=True, edgecolor='none', facecolor='yellow', alpha=0.3, zorder=2))
    top_y_center_pixel_val = current_top_y_offset * minimap_height
    top_y_center_line = ax.plot([0, minimap_width], [top_y_center_pixel_val, top_y_center_pixel_val], 'y--', lw=1, label='Top-Y C', zorder=3)
    top_y_upper_line = ax.plot([0, minimap_width], [(current_top_y_offset + current_top_y_threshold) * minimap_height] * 2, 'y-', lw=0.8, alpha=0.7, zorder=3)
    top_y_lower_line = ax.plot([0, minimap_width], [(current_top_y_offset - current_top_y_threshold) * minimap_height] * 2, 'y-', lw=0.8, alpha=0.7, zorder=3)

    # --- Draw Top Lane Vertical Band ---
    top_x_verts_pixel = [
        ((current_top_x_offset - current_top_x_threshold) * minimap_width, 0 * minimap_height),
        ((current_top_x_offset + current_top_x_threshold) * minimap_width, 0 * minimap_height),
        ((current_top_x_offset + current_top_x_threshold) * minimap_width, 1 * minimap_height),
        ((current_top_x_offset - current_top_x_threshold) * minimap_width, 1 * minimap_height),
    ]
    top_x_band_patch = ax.add_patch(patches.Polygon(top_x_verts_pixel, closed=True, edgecolor='none', facecolor='lime', alpha=0.3, zorder=2))
    top_x_center_pixel_val = current_top_x_offset * minimap_width
    top_x_center_line = ax.plot([top_x_center_pixel_val, top_x_center_pixel_val], [0, minimap_height], 'g--', lw=1, label='Top-X C', zorder=3)
    top_x_right_line = ax.plot([(current_top_x_offset + current_top_x_threshold) * minimap_width] * 2, [0, minimap_height], 'g-', lw=0.8, alpha=0.7, zorder=3)
    top_x_left_line = ax.plot([(current_top_x_offset - current_top_x_threshold) * minimap_width] * 2, [0, minimap_height], 'g-', lw=0.8, alpha=0.7, zorder=3)

    # --- Draw Bot Lane Horizontal Band ---
    bot_y_verts_pixel = [
        (0 * minimap_width, (current_bot_y_offset - current_bot_y_threshold) * minimap_height),
        (1 * minimap_width, (current_bot_y_offset - current_bot_y_threshold) * minimap_height),
        (1 * minimap_width, (current_bot_y_offset + current_bot_y_threshold) * minimap_height),
        (0 * minimap_width, (current_bot_y_offset + current_bot_y_threshold) * minimap_height),
    ]
    bot_y_band_patch = ax.add_patch(patches.Polygon(bot_y_verts_pixel, closed=True, edgecolor='none', facecolor='orange', alpha=0.3, zorder=2))
    bot_y_center_pixel_val = current_bot_y_offset * minimap_height
    bot_y_center_line = ax.plot([0, minimap_width], [bot_y_center_pixel_val, bot_y_center_pixel_val], color='chocolate', linestyle='--', lw=1, label='Bot-Y C', zorder=3)
    bot_y_upper_line = ax.plot([0, minimap_width], [(current_bot_y_offset + current_bot_y_threshold) * minimap_height] * 2, color='chocolate', linestyle='-', lw=0.8, alpha=0.7, zorder=3)
    bot_y_lower_line = ax.plot([0, minimap_width], [(current_bot_y_offset - current_bot_y_threshold) * minimap_height] * 2, color='chocolate', linestyle='-', lw=0.8, alpha=0.7, zorder=3)

    # --- Draw Bot Lane Vertical Band ---
    bot_x_verts_pixel = [
        ((current_bot_x_offset - current_bot_x_threshold) * minimap_width, 0 * minimap_height),
        ((current_bot_x_offset + current_bot_x_threshold) * minimap_width, 0 * minimap_height),
        ((current_bot_x_offset + current_bot_x_threshold) * minimap_width, 1 * minimap_height),
        ((current_bot_x_offset - current_bot_x_threshold) * minimap_width, 1 * minimap_height),
    ]
    bot_x_band_patch = ax.add_patch(patches.Polygon(bot_x_verts_pixel, closed=True, edgecolor='none', facecolor='pink', alpha=0.3, zorder=2))
    bot_x_center_pixel_val = current_bot_x_offset * minimap_width
    bot_x_center_line = ax.plot([bot_x_center_pixel_val, bot_x_center_pixel_val], [0, minimap_height], color='deeppink', linestyle='--', lw=1, label='Bot-X C', zorder=3)
    bot_x_right_line = ax.plot([(current_bot_x_offset + current_bot_x_threshold) * minimap_width] * 2, [0, minimap_height], color='deeppink', linestyle='-', lw=0.8, alpha=0.7, zorder=3)
    bot_x_left_line = ax.plot([(current_bot_x_offset - current_bot_x_threshold) * minimap_width] * 2, [0, minimap_height], color='deeppink', linestyle='-', lw=0.8, alpha=0.7, zorder=3)
    
    title_str = (f"MidTh:{current_mid_threshold:.2f} MOY:{current_mid_offset_y:.2f} | "
                 f"TYO:{current_top_y_offset:.2f} TYTh:{current_top_y_threshold:.2f} | "
                 f"TXO:{current_top_x_offset:.2f} TXTh:{current_top_x_threshold:.2f}\n"
                 f"BYO:{current_bot_y_offset:.2f} BYTh:{current_bot_y_threshold:.2f} | "
                 f"BXO:{current_bot_x_offset:.2f} BXTh:{current_bot_x_threshold:.2f}")
    ax.set_title(title_str, fontsize='small')
    ax.set_xlim(0, minimap_width)
    ax.set_ylim(minimap_height, 0) 

    handles, labels = ax.get_legend_handles_labels()
    unique_labels_dict = {}
    unique_handles = []
    for handle, label in zip(handles, labels):
        if label not in unique_labels_dict:
            unique_labels_dict[label] = handle
            unique_handles.append(handle)
    if unique_handles:
        ax.legend(unique_handles, unique_labels_dict.keys(), fontsize='xx-small', loc='lower center', ncol=3) # Adjusted legend

    fig.canvas.draw_idle()

def main():
    global minimap_width, minimap_height, fig, ax
    global current_mid_threshold, current_mid_offset_y
    global current_top_y_offset, current_top_y_threshold, current_top_x_offset, current_top_x_threshold
    global current_bot_y_offset, current_bot_y_threshold, current_bot_x_offset, current_bot_x_threshold

    try:
        img = mpimg.imread(MINIMAP_IMAGE_PATH)
    except FileNotFoundError:
        print(f"ERROR: Image file not found at '{MINIMAP_IMAGE_PATH}'")
        exit()
    except Exception as e:
        print(f"ERROR: Could not load image. {e}")
        exit()

    if img.ndim == 3:
        minimap_height, minimap_width, _ = img.shape
    elif img.ndim == 2:
        minimap_height, minimap_width = img.shape
    else:
        print("ERROR: Unsupported image format/dimensions.")
        exit()

    print(f"Minimap loaded: Width={minimap_width}px, Height={minimap_height}px")
    print("Click on the minimap to get coordinates and lane classification.")
    print("Enter commands in the console to adjust lane parameters.")
    print("Close the plot window to exit the script.")

    fig, ax = plt.subplots(figsize=(10, 11)) # Adjusted figure size for title
    ax.imshow(img, zorder=1)

    fig.canvas.mpl_connect('button_press_event', onclick)
    update_visuals()
    
    plt.ion()
    plt.show()

    param_map = {
        "mthr": "Mid Threshold", "moffy": "Mid Offset Y",
        "tyoff": "Top Y Offset", "tythr": "Top Y Threshold",
        "txoff": "Top X Offset", "txthr": "Top X Threshold",
        "byoff": "Bot Y Offset", "bythr": "Bot Y Threshold",
        "bxoff": "Bot X Offset", "bxthr": "Bot X Threshold"
    }
    current_values_map = lambda: {
        "mthr": current_mid_threshold, "moffy": current_mid_offset_y,
        "tyoff": current_top_y_offset, "tythr": current_top_y_threshold,
        "txoff": current_top_x_offset, "txthr": current_top_x_threshold,
        "byoff": current_bot_y_offset, "bythr": current_bot_y_threshold,
        "bxoff": current_bot_x_offset, "bxthr": current_bot_x_threshold
    }

    try:
        while True:
            if not plt.fignum_exists(fig.number):
                print("Plot window closed. Exiting input loop.")
                break
            
            print("\nAvailable parameters to adjust:")
            for k, v in param_map.items():
                print(f"  {k}: {v} (current: {current_values_map()[k]:.3f})")
            
            choice = input("Enter param code to change (e.g., 'mthr'), or 'q' to quit: ").lower().strip()

            if choice == 'q':
                break
            
            if choice in param_map:
                try:
                    new_val_str = input(f"Enter new value for {param_map[choice]}: ")
                    new_val = float(new_val_str)
                    
                    if "thr" in choice and (new_val < 0 or new_val > 0.2): # Adjusted max threshold
                        print("Thresholds should generally be between 0.0 and 0.2.")
                        continue
                    if "off" in choice and (new_val < -0.2 or new_val > 1.2):
                        print("Offsets should generally be near 0.0 to 1.0.")
                        continue
                    
                    if choice == "mthr": current_mid_threshold = new_val
                    elif choice == "moffy": current_mid_offset_y = new_val
                    elif choice == "tyoff": current_top_y_offset = new_val
                    elif choice == "tythr": current_top_y_threshold = new_val
                    elif choice == "txoff": current_top_x_offset = new_val
                    elif choice == "txthr": current_top_x_threshold = new_val
                    elif choice == "byoff": current_bot_y_offset = new_val
                    elif choice == "bythr": current_bot_y_threshold = new_val
                    elif choice == "bxoff": current_bot_x_offset = new_val
                    elif choice == "bxthr": current_bot_x_threshold = new_val
                    
                    update_visuals()
                except ValueError:
                    print("Invalid numeric value entered.")
                except Exception as e:
                    print(f"An error occurred: {e}")
            else:
                print("Invalid parameter code. Please choose from the list.")
            
            plt.pause(0.01)

    except KeyboardInterrupt:
        print("\nExiting due to Ctrl+C.")
    finally:
        plt.ioff()
        print("Script finished.")

if __name__ == "__main__":
    main()