Gemini said
Based on the project specification for Tank Battle: Chaos Maze, here is the comprehensive list of work and requirements for the game:

1. Technical Foundation & Setup

Engine Choice: Utilize any 2D game engine that supports direct pixel or sprite manipulation.
+1


Asset Management: Acquire and implement external sprites for the tank bodies, turrets, walls, and bullets.


Map System: Create a level layout (maze) using a 2D array, grid, or text-based tilemap approach.
+1

2. Tank Mechanics & Physics

Input Handling: Implement simultaneous local multiplayer controls for two players on one keyboard.


Player 1: WASD for movement/rotation and Space or F for shooting.


Player 2: Arrow Keys for movement/rotation and Enter or M for shooting.


Vector Movement: Calculate velocity based on rotation angle and speed using trigonometry.
+1


velocity.x=speed×cos(θ).


velocity.y=speed×sin(θ).


Sprite Transformations: Handle 2D rotations for both the tank body and the turret around their center points.


Collision Detection: Implement AABB (Axis-Aligned Bounding Box) or Mask-based collision to ensure tanks stop when hitting walls.

3. Weaponry & Ballistics (Physics Core)

Projectile Spawning: Ensure bullets spawn at the tip of the tank's turret or barrel.


Reflection Physics: Program bullets to bounce off walls based on the surface normal vector using the formula: 

Vnew = Vold − 2( Vold ⋅ n ) n

Combat Logic: Implement hit detection where bullets damage or destroy enemy tanks.
+1


Fire Rate Control: Limit the number of bullets on screen (e.g., 5 per player) or implement a cooldown to prevent spamming.

4. Game Flow & User Interface

Start Screen: Create a title screen with a "Press Start" prompt.


Gameplay Loop: Spawn players at opposite corners of the maze and manage round endings based on tank destruction or score limits.


Game Over Screen: Display the winner (Player 1 or Player 2) and provide an option to restart the game.


HUD (Heads-Up Display): Clearly display health and scores for both players in the top corners of the screen.

5. Submission & Documentation

GitHub Repository: Host the source code on a public link and submit it via LMS.


README Documentation: Include an explanation of the physics implementation (specifically reflection), control instructions, and asset citations.


Presentation: Prepare a gameplay demo and be ready to explain the specific code blocks used for collision.

6. Bonus Extensions (High-Distinction Features)

Independent Turret Rotation: Decouple turret rotation from the tank body using mouse input or separate keys.


Destructible Environment: Create walls that can be destroyed by bullet fire.


Power-up System: Randomly spawn items like Speed Up, Shields, or Triple Shot.


Visual Effects: Implement particle systems or sprites for explosions when tanks are destroyed.


Audio Implementation: Add sound effects for shooting, bouncing, and explosions.