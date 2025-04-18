import pygame

pygame.mixer.init()

(HITSOUND := pygame.mixer.Sound('ui/assets/sounds/explosion.wav')).set_volume(0.05)
(SHOTSOUND := pygame.mixer.Sound('ui/assets/sounds/explosion.wav')).set_volume(0.05)
(MISSSOUND := pygame.mixer.Sound('ui/assets/sounds/explosion.wav')).set_volume(0.05)
