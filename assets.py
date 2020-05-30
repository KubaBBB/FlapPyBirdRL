import pygame


def get_assets():
    IMAGES, SOUNDS, HIT_MASKS = {}, {}, {}

    PLAYER = (
            'assets/sprites/redbird-upflap.png',
            'assets/sprites/redbird-midflap.png',
            'assets/sprites/redbird-downflap.png',
    )

    BACKGROUND = 'assets/sprites/background-night.png'
    PIPE = 'assets/sprites/pipe-green.png'

    IMAGES['numbers'] = (
            pygame.image.load('assets/sprites/0.png').convert_alpha(),
            pygame.image.load('assets/sprites/1.png').convert_alpha(),
            pygame.image.load('assets/sprites/2.png').convert_alpha(),
            pygame.image.load('assets/sprites/3.png').convert_alpha(),
            pygame.image.load('assets/sprites/4.png').convert_alpha(),
            pygame.image.load('assets/sprites/5.png').convert_alpha(),
            pygame.image.load('assets/sprites/6.png').convert_alpha(),
            pygame.image.load('assets/sprites/7.png').convert_alpha(),
            pygame.image.load('assets/sprites/8.png').convert_alpha(),
            pygame.image.load('assets/sprites/9.png').convert_alpha()
        )

    IMAGES['gameover'] = pygame.image.load('assets/sprites/gameover.png').convert_alpha()

    IMAGES['base'] = pygame.image.load('assets/sprites/base.png').convert_alpha()

    soundExt = '.wav'

    SOUNDS['die'] = pygame.mixer.Sound('assets/audio/die' + soundExt)
    SOUNDS['hit'] = pygame.mixer.Sound('assets/audio/hit' + soundExt)
    SOUNDS['point'] = pygame.mixer.Sound('assets/audio/point' + soundExt)
    SOUNDS['swoosh'] = pygame.mixer.Sound('assets/audio/swoosh' + soundExt)
    SOUNDS['wing'] = pygame.mixer.Sound('assets/audio/wing' + soundExt)

    IMAGES['background'] = pygame.image.load(BACKGROUND).convert()
    IMAGES['player'] = (
        pygame.image.load(PLAYER[0]).convert_alpha(),
        pygame.image.load(PLAYER[1]).convert_alpha(),
        pygame.image.load(PLAYER[2]).convert_alpha(),
    )
    IMAGES['pipe'] = (
        pygame.transform.flip(
            pygame.image.load(PIPE).convert_alpha(), False, True),
        pygame.image.load(PIPE).convert_alpha(),
    )

    # hismask for pipes
    HIT_MASKS['pipe'] = (
        get_hitmask(IMAGES['pipe'][0]),
        get_hitmask(IMAGES['pipe'][1]),
    )

    # hitmask for player
    HIT_MASKS['player'] = (
        get_hitmask(IMAGES['player'][0]),
        get_hitmask(IMAGES['player'][1]),
        get_hitmask(IMAGES['player'][2]),
    )

    return IMAGES, SOUNDS, HIT_MASKS


def get_hitmask(image):
    """returns a hitmask using an image's alpha."""
    mask = []
    for x in range(image.get_width()):
        mask.append([])
        for y in range(image.get_height()):
            mask[x].append(bool(image.get_at((x, y))[3]))
    return mask