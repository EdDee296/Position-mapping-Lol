import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as patches
import numpy as np

# --- CONFIGURATION ---
MINIMAP_IMAGE_PATH = "C:/Users/ASUS/OneDrive/New folder/a.png"  # Use your path

# Mid Lane (Diagonal: y = slope*x + intercept)
INITIAL_MID_THRESHOLD = 0.05
INITIAL_MID_SLOPE = -1.0
INITIAL_MID_INTERCEPT = 1.0 + 0.05 # Was 1.0 + INITIAL_MID_OFFSET_Y

# Top Lane Horizontal (Line: y = offset_y)
INITIAL_TOP_Y_OFFSET = 0.13
INITIAL_TOP_Y_THRESHOLD = 0.03

# Top Lane Vertical (Line: x = offset_x)
INITIAL_TOP_X_OFFSET = 0.13
INITIAL_TOP_X_THRESHOLD = 0.03

# Bot Lane Horizontal (Line: y = offset_y, near bottom)
INITIAL_BOT_Y_OFFSET = 0.905
INITIAL_BOT_Y_THRESHOLD = 0.03

# Bot Lane Vertical (Line: x = offset_x, near right)
INITIAL_BOT_X_OFFSET = 0.905
INITIAL_BOT_X_THRESHOLD = 0.03

# River (Diagonal: y = slope*x + intercept)
INITIAL_RIVER_THRESHOLD = 0.07
INITIAL_RIVER_SLOPE = 0.97
INITIAL_RIVER_INTERCEPT = 0.00 # Was INITIAL_RIVER_OFFSET_Y

BASE_RADIUS = 0.4


# --- GLOBAL VARIABLES ---
minimap_width = 0
minimap_height = 0
fig = None
ax = None

# Mid Lane
current_mid_threshold = INITIAL_MID_THRESHOLD
current_mid_slope = INITIAL_MID_SLOPE
current_mid_intercept = INITIAL_MID_INTERCEPT
mid_band_patch, mid_center_line, mid_upper_line, mid_lower_line = None, None, None, None

# Top Lane (same as before)
current_top_y_offset = INITIAL_TOP_Y_OFFSET
current_top_y_threshold = INITIAL_TOP_Y_THRESHOLD
top_y_band_patch, top_y_center_line, top_y_upper_line, top_y_lower_line = None, None, None, None
current_top_x_offset = INITIAL_TOP_X_OFFSET
current_top_x_threshold = INITIAL_TOP_X_THRESHOLD
top_x_band_patch, top_x_center_line, top_x_right_line, top_x_left_line = None, None, None, None

# Bot Lane (same as before)
current_bot_y_offset = INITIAL_BOT_Y_OFFSET
current_bot_y_threshold = INITIAL_BOT_Y_THRESHOLD
bot_y_band_patch, bot_y_center_line, bot_y_upper_line, bot_y_lower_line = None, None, None, None
current_bot_x_offset = INITIAL_BOT_X_OFFSET
current_bot_x_threshold = INITIAL_BOT_X_THRESHOLD
bot_x_band_patch, bot_x_center_line, bot_x_right_line, bot_x_left_line = None, None, None, None

# River
current_river_threshold = INITIAL_RIVER_THRESHOLD
current_river_slope = INITIAL_RIVER_SLOPE
current_river_intercept = INITIAL_RIVER_INTERCEPT
river_band_patch, river_center_line, river_upper_line, river_lower_line = None, None, None, None

# Base circles
left_base_circle_patch = None
right_base_circle_patch = None


# --- FUNCTIONS ---
def clear_artist(artist):
    if artist:
        if isinstance(artist, list) and artist:
            if artist[0] in ax.lines: artist.pop(0).remove()
        elif artist in ax.patches:
            artist.remove()
    return None

def onclick(event):
    global minimap_width, minimap_height
    global current_mid_threshold, current_mid_slope, current_mid_intercept
    global current_top_y_offset, current_top_y_threshold, current_top_x_offset, current_top_x_threshold
    global current_bot_y_offset, current_bot_y_threshold, current_bot_x_offset, current_bot_x_threshold
    global current_river_threshold, current_river_slope, current_river_intercept
    global BASE_RADIUS

    if event.inaxes == ax and event.xdata is not None and event.ydata is not None:
        pixel_x = int(round(event.xdata))
        pixel_y = int(round(event.ydata))
        pixel_x = max(0, min(pixel_x, minimap_width - 1))
        pixel_y = max(0, min(pixel_y, minimap_height - 1))
        norm_x = pixel_x / minimap_width
        norm_y = pixel_y / minimap_height
        
        dist_left_base = np.sqrt((norm_x - 0)**2 + (norm_y - 1)**2)
        dist_right_base = np.sqrt((norm_x - 1)**2 + (norm_y - 0)**2)
        
        location_found = False
        if dist_left_base <= BASE_RADIUS:
            print("Left Base")
            location_found = True
        elif dist_right_base <= BASE_RADIUS:
            print("Right Base")
            location_found = True
        
        if not location_found:
            mid_center_y_val = current_mid_slope * norm_x + current_mid_intercept
            is_in_mid = (mid_center_y_val - current_mid_threshold <= norm_y <= 
                         mid_center_y_val + current_mid_threshold)
            if is_in_mid:
                print("Mid Lane")
                location_found = True

        if not location_found:
            is_in_top_y = (current_top_y_offset - current_top_y_threshold <= norm_y <=
                           current_top_y_offset + current_top_y_threshold)
            is_in_top_x = (current_top_x_offset - current_top_x_threshold <= norm_x <=
                           current_top_x_offset + current_top_x_threshold)
            if is_in_top_y or is_in_top_x: 
                print("Top Lane")
                location_found = True
        
        if not location_found:
            is_in_bot_y = (current_bot_y_offset - current_bot_y_threshold <= norm_y <=
                           current_bot_y_offset + current_bot_y_threshold)
            is_in_bot_x = (current_bot_x_offset - current_bot_x_threshold <= norm_x <=
                           current_bot_x_offset + current_bot_x_threshold)
            if is_in_bot_y or is_in_bot_x:
                print("Bot Lane")
                location_found = True

        if not location_found:
            river_center_y_val = current_river_slope * norm_x + current_river_intercept
            is_in_river_band = (river_center_y_val - current_river_threshold <= norm_y <=
                                river_center_y_val + current_river_threshold)
            if is_in_river_band:
                mid_line_y_at_river_x = current_mid_slope * norm_x + current_mid_intercept
                if norm_y < mid_line_y_at_river_x: # Comparing y value to the mid lane's line
                    print("Top River")
                else:
                    print("Bot River")
                location_found = True
        
        if not location_found:
            # If not in any defined region, classify as jungle
            y_on_mid_line = current_mid_slope * norm_x + current_mid_intercept
            y_on_river_line = current_river_slope * norm_x + current_river_intercept

            is_above_mid_line = norm_y < y_on_mid_line
            is_above_river_line = norm_y < y_on_river_line 

            if is_above_mid_line:
                if is_above_river_line:
                    print("Top-Right Jungle (Red Top)")
                else: # Below river line (norm_y >= y_on_river_line)
                    print("Top-Left Jungle (Blue Top)")
            else: # Below mid line (norm_y >= y_on_mid_line)
                if is_above_river_line:
                    print("Bot-Right Jungle (Red Bot)")
                else: # Below river line
                    print("Bot-Left Jungle (Blue Bot)")
            location_found = True # Classified as jungle

        if not location_found: # This case should ideally not be reached if jungle is the catch-all
            print(
                f"Unclassified: Pixel (x={pixel_x}, y={pixel_y}) | Normalized (nx={norm_x:.3f}, ny={norm_y:.3f})")

def update_visuals():
    global mid_band_patch, mid_center_line # Removed mid_upper/lower_line for simplicity with slope
    global top_y_band_patch, top_y_center_line
    global top_x_band_patch, top_x_center_line
    global bot_y_band_patch, bot_y_center_line
    global bot_x_band_patch, bot_x_center_line
    global river_band_patch, river_center_line # Removed river_upper/lower_line
    global left_base_circle_patch, right_base_circle_patch
    global minimap_width, minimap_height, ax, fig
    global current_mid_threshold, current_mid_slope, current_mid_intercept
    global current_top_y_offset, current_top_y_threshold, current_top_x_offset, current_top_x_threshold
    global current_bot_y_offset, current_bot_y_threshold, current_bot_x_offset, current_bot_x_threshold
    global current_river_threshold, current_river_slope, current_river_intercept
    global BASE_RADIUS

    # --- Clear previous artists ---
    artists_to_clear = [
        mid_band_patch, mid_center_line, 
        top_y_band_patch, top_y_center_line, 
        top_x_band_patch, top_x_center_line, 
        bot_y_band_patch, bot_y_center_line, 
        bot_x_band_patch, bot_x_center_line, 
        river_band_patch, river_center_line, 
        left_base_circle_patch, right_base_circle_patch
    ]
    # Specific handling for lines that were removed from globals
    global mid_upper_line, mid_lower_line, river_upper_line, river_lower_line 
    global top_y_upper_line, top_y_lower_line, top_x_right_line, top_x_left_line
    global bot_y_upper_line, bot_y_lower_line, bot_x_right_line, bot_x_left_line
    
    mid_upper_line = clear_artist(mid_upper_line)
    mid_lower_line = clear_artist(mid_lower_line)
    river_upper_line = clear_artist(river_upper_line)
    river_lower_line = clear_artist(river_lower_line)
    top_y_upper_line = clear_artist(top_y_upper_line); top_y_lower_line = clear_artist(top_y_lower_line)
    top_x_right_line = clear_artist(top_x_right_line); top_x_left_line = clear_artist(top_x_left_line)
    bot_y_upper_line = clear_artist(bot_y_upper_line); bot_y_lower_line = clear_artist(bot_y_lower_line)
    bot_x_right_line = clear_artist(bot_x_right_line); bot_x_left_line = clear_artist(bot_x_left_line)


    (mid_band_patch, mid_center_line, 
     top_y_band_patch, top_y_center_line, 
     top_x_band_patch, top_x_center_line, 
     bot_y_band_patch, bot_y_center_line, 
     bot_x_band_patch, bot_x_center_line, 
     river_band_patch, river_center_line, 
     left_base_circle_patch, right_base_circle_patch) = [clear_artist(art) for art in artists_to_clear]


    # --- Draw Base Circles ---
    left_base_circle_patch = ax.add_patch(patches.Circle((0, minimap_height), BASE_RADIUS * min(minimap_width, minimap_height), edgecolor='blue', facecolor='dodgerblue', alpha=0.3, zorder=1.5, label='Left Base'))
    right_base_circle_patch = ax.add_patch(patches.Circle((minimap_width, 0), BASE_RADIUS * min(minimap_width, minimap_height), edgecolor='red', facecolor='salmon', alpha=0.3, zorder=1.5, label='Right Base'))

    norm_x_coords = np.array([0, 1])
    center_x_pixel = norm_x_coords * minimap_width

    # --- Draw Mid Lane Band (y = m*x + c) ---
    # Polygon vertices for y = slope*x + intercept +/- threshold
    mid_y_at_x0_lower = (current_mid_slope * 0 + current_mid_intercept - current_mid_threshold) * minimap_height
    mid_y_at_x1_lower = (current_mid_slope * 1 + current_mid_intercept - current_mid_threshold) * minimap_height
    mid_y_at_x1_upper = (current_mid_slope * 1 + current_mid_intercept + current_mid_threshold) * minimap_height
    mid_y_at_x0_upper = (current_mid_slope * 0 + current_mid_intercept + current_mid_threshold) * minimap_height
    mid_verts_pixel = [
        (0 * minimap_width, mid_y_at_x0_lower),
        (1 * minimap_width, mid_y_at_x1_lower),
        (1 * minimap_width, mid_y_at_x1_upper),
        (0 * minimap_width, mid_y_at_x0_upper),
    ]
    mid_band_patch = ax.add_patch(patches.Polygon(mid_verts_pixel, closed=True, edgecolor='none', facecolor='cyan', alpha=0.3, zorder=2))
    mid_center_y_pixel = (current_mid_slope * norm_x_coords + current_mid_intercept) * minimap_height
    mid_center_line = ax.plot(center_x_pixel, mid_center_y_pixel, 'm--', lw=1, label='Mid C', zorder=3)

    # --- Draw River Band (y = m*x + c) ---
    river_y_at_x0_lower = (current_river_slope * 0 + current_river_intercept - current_river_threshold) * minimap_height
    river_y_at_x1_lower = (current_river_slope * 1 + current_river_intercept - current_river_threshold) * minimap_height
    river_y_at_x1_upper = (current_river_slope * 1 + current_river_intercept + current_river_threshold) * minimap_height
    river_y_at_x0_upper = (current_river_slope * 0 + current_river_intercept + current_river_threshold) * minimap_height
    river_verts_pixel = [
        (0 * minimap_width, river_y_at_x0_lower),
        (1 * minimap_width, river_y_at_x1_lower),
        (1 * minimap_width, river_y_at_x1_upper),
        (0 * minimap_width, river_y_at_x0_upper),
    ]
    river_band_patch = ax.add_patch(patches.Polygon(river_verts_pixel, closed=True, edgecolor='none', facecolor='deepskyblue', alpha=0.25, zorder=1.8))
    river_center_y_pixel = (current_river_slope * norm_x_coords + current_river_intercept) * minimap_height
    river_center_line = ax.plot(center_x_pixel, river_center_y_pixel, color='blue', linestyle='--', lw=1, label='River C', zorder=3)

    # --- Top & Bot Lane (Horizontal/Vertical - No change in drawing logic) ---
    top_y_verts_pixel = [ (0, (current_top_y_offset - current_top_y_threshold) * minimap_height), (minimap_width, (current_top_y_offset - current_top_y_threshold) * minimap_height), (minimap_width, (current_top_y_offset + current_top_y_threshold) * minimap_height), (0, (current_top_y_offset + current_top_y_threshold) * minimap_height), ]
    top_y_band_patch = ax.add_patch(patches.Polygon(top_y_verts_pixel, closed=True, edgecolor='none', facecolor='yellow', alpha=0.3, zorder=2))
    top_y_center_pixel_val = current_top_y_offset * minimap_height
    top_y_center_line = ax.plot([0, minimap_width], [top_y_center_pixel_val, top_y_center_pixel_val], 'y--', lw=1, label='TopY C', zorder=3)

    top_x_verts_pixel = [ ((current_top_x_offset - current_top_x_threshold) * minimap_width, 0), ((current_top_x_offset + current_top_x_threshold) * minimap_width, 0), ((current_top_x_offset + current_top_x_threshold) * minimap_width, minimap_height), ((current_top_x_offset - current_top_x_threshold) * minimap_width, minimap_height), ]
    top_x_band_patch = ax.add_patch(patches.Polygon(top_x_verts_pixel, closed=True, edgecolor='none', facecolor='lime', alpha=0.3, zorder=2))
    top_x_center_pixel_val = current_top_x_offset * minimap_width
    top_x_center_line = ax.plot([top_x_center_pixel_val, top_x_center_pixel_val], [0, minimap_height], 'g--', lw=1, label='TopX C', zorder=3)

    bot_y_verts_pixel = [ (0, (current_bot_y_offset - current_bot_y_threshold) * minimap_height), (minimap_width, (current_bot_y_offset - current_bot_y_threshold) * minimap_height), (minimap_width, (current_bot_y_offset + current_bot_y_threshold) * minimap_height), (0, (current_bot_y_offset + current_bot_y_threshold) * minimap_height), ]
    bot_y_band_patch = ax.add_patch(patches.Polygon(bot_y_verts_pixel, closed=True, edgecolor='none', facecolor='orange', alpha=0.3, zorder=2))
    bot_y_center_pixel_val = current_bot_y_offset * minimap_height
    bot_y_center_line = ax.plot([0, minimap_width], [bot_y_center_pixel_val, bot_y_center_pixel_val], color='chocolate', linestyle='--', lw=1, label='BotY C', zorder=3)

    bot_x_verts_pixel = [ ((current_bot_x_offset - current_bot_x_threshold) * minimap_width, 0), ((current_bot_x_offset + current_bot_x_threshold) * minimap_width, 0), ((current_bot_x_offset + current_bot_x_threshold) * minimap_width, minimap_height), ((current_bot_x_offset - current_bot_x_threshold) * minimap_width, minimap_height), ]
    bot_x_band_patch = ax.add_patch(patches.Polygon(bot_x_verts_pixel, closed=True, edgecolor='none', facecolor='pink', alpha=0.3, zorder=2))
    bot_x_center_pixel_val = current_bot_x_offset * minimap_width
    bot_x_center_line = ax.plot([bot_x_center_pixel_val, bot_x_center_pixel_val], [0, minimap_height], color='deeppink', linestyle='--', lw=1, label='BotX C', zorder=3)
    
    title_str = (f"MTh:{current_mid_threshold:.2f} MSlp:{current_mid_slope:.2f} MInt:{current_mid_intercept:.2f} | "
                 f"TYO:{current_top_y_offset:.2f} TYTh:{current_top_y_threshold:.2f} | "
                 f"TXO:{current_top_x_offset:.2f} TXTh:{current_top_x_threshold:.2f}\n"
                 f"BYO:{current_bot_y_offset:.2f} BYTh:{current_bot_y_threshold:.2f} | "
                 f"BXO:{current_bot_x_offset:.2f} BXTh:{current_bot_x_threshold:.2f}\n"
                 f"RTh:{current_river_threshold:.2f} RSlp:{current_river_slope:.2f} RInt:{current_river_intercept:.2f} | BR:{BASE_RADIUS:.2f}")
    ax.set_title(title_str, fontsize=8)
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
        ax.legend(unique_handles, unique_labels_dict.keys(), fontsize=6, loc='lower center', ncol=4)

    fig.canvas.draw_idle()

def main():
    global minimap_width, minimap_height, fig, ax
    global current_mid_threshold, current_mid_slope, current_mid_intercept
    global current_top_y_offset, current_top_y_threshold, current_top_x_offset, current_top_x_threshold
    global current_bot_y_offset, current_bot_y_threshold, current_bot_x_offset, current_bot_x_threshold
    global current_river_threshold, current_river_slope, current_river_intercept
    global BASE_RADIUS

    try:
        img = mpimg.imread(MINIMAP_IMAGE_PATH)
    except FileNotFoundError:
        print(f"ERROR: Image file not found at '{MINIMAP_IMAGE_PATH}'")
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

    fig, ax = plt.subplots(figsize=(10, 12))
    ax.imshow(img, zorder=1)

    fig.canvas.mpl_connect('button_press_event', onclick)
    update_visuals()
    
    plt.ion()
    plt.show()

    param_map = {
        "mthr": "Mid Threshold", "mslp": "Mid Slope", "mint": "Mid Intercept",
        "tyoff": "Top Y Offset", "tythr": "Top Y Threshold",
        "txoff": "Top X Offset", "txthr": "Top X Threshold",
        "byoff": "Bot Y Offset", "bythr": "Bot Y Threshold",
        "bxoff": "Bot X Offset", "bxthr": "Bot X Threshold",
        "rthr": "River Threshold", "rslp": "River Slope", "rint": "River Intercept",
        "br": "Base Radius"
    }
    current_values_map = lambda: {
        "mthr": current_mid_threshold, "mslp": current_mid_slope, "mint": current_mid_intercept,
        "tyoff": current_top_y_offset, "tythr": current_top_y_threshold,
        "txoff": current_top_x_offset, "txthr": current_top_x_threshold,
        "byoff": current_bot_y_offset, "bythr": current_bot_y_threshold,
        "bxoff": current_bot_x_offset, "bxthr": current_bot_x_threshold,
        "rthr": current_river_threshold, "rslp": current_river_slope, "rint": current_river_intercept,
        "br": BASE_RADIUS
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
                    
                    valid_input = True
                    if "thr" in choice and (new_val < 0 or new_val > 0.25):
                        print("Thresholds should generally be between 0.0 and 0.25.")
                        valid_input = False
                    # Slope can be negative or positive, e.g., -2 to 2
                    elif "slp" in choice and (new_val < -5 or new_val > 5):
                        print("Slopes should generally be between -5.0 and 5.0 for reasonable angles.")
                        valid_input = False
                    # Intercepts can also vary more widely
                    elif "int" in choice and (new_val < -1 or new_val > 2): # y-intercept when x=0
                        print("Intercepts should generally be between -1.0 and 2.0.")
                        valid_input = False
                    elif choice == "br" and (new_val < 0.05 or new_val > 0.5):
                        print("Base Radius should be between 0.05 and 0.5.")
                        valid_input = False
                    # Add specific checks for Top/Bot offsets if needed, e.g., tyoff should be 0 to 0.5
                    
                    if not valid_input:
                        continue
                        
                    if choice == "mthr": current_mid_threshold = new_val
                    elif choice == "mslp": current_mid_slope = new_val
                    elif choice == "mint": current_mid_intercept = new_val
                    elif choice == "tyoff": current_top_y_offset = new_val
                    elif choice == "tythr": current_top_y_threshold = new_val
                    elif choice == "txoff": current_top_x_offset = new_val
                    elif choice == "txthr": current_top_x_threshold = new_val
                    elif choice == "byoff": current_bot_y_offset = new_val
                    elif choice == "bythr": current_bot_y_threshold = new_val
                    elif choice == "bxoff": current_bot_x_offset = new_val
                    elif choice == "bxthr": current_bot_x_threshold = new_val
                    elif choice == "rthr": current_river_threshold = new_val
                    elif choice == "rslp": current_river_slope = new_val
                    elif choice == "rint": current_river_intercept = new_val
                    elif choice == "br": BASE_RADIUS = new_val
                    
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