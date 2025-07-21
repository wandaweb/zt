# NiNa's Note Feature Implementation

## Overview
Added a special pink rectangle obstacle to level 4 (Upper Crust) that, when destroyed, reveals a hidden message from NiNa. The note can be viewed from the victory screen after completing the game.

## Changes Made

1. **Added NiNaNote Class**
   - Created a new class to represent the special pink rectangle obstacle
   - Implemented health, damage, and destruction mechanics
   - Added visual styling with pink color

2. **Game State Variables**
   - Added `nina_note_found` to track if the player found the note
   - Added `nina_note_message_timer` to control how long the discovery message appears
   - Added `show_nina_note` to control the note display screen
   - Added `nina_note` to store the actual note object
   - Added `nina_note_spawned` to ensure the note only spawns once

3. **Spawning Logic**
   - Added code to spawn the note in layer 4 (Upper Crust)
   - Note spawns in the first half of the layer at a random position

4. **Collision Detection**
   - Updated collision detection to handle player bullets and drill hitting the note
   - When destroyed, sets `nina_note_found` to true and shows a message

5. **UI Elements**
   - Added "Found NiNa's note" message that appears at the top of the screen when the note is found
   - Added "Press N to read NiNa's note" option on the victory screen (in light pink)
   - Created a new screen to display the note's contents

6. **Note Content**
   - Added NiNa's message about a repair station hidden in the Myst nebula
   - Included blinking coordinates for visual effect

7. **Input Handling**
   - Added handling for the 'N' key on the victory screen to view the note
   - Added handling to exit the note screen with any key press

8. **Game Reset**
   - Updated the restart_game method to reset all NiNa's note related variables

## Testing
The feature has been tested and works as expected:
- The pink rectangle appears in level 4
- When destroyed, a message appears at the top of the screen
- The victory screen shows the option to read the note
- Pressing N shows the note screen with the message
- Any key press returns to the victory screen
