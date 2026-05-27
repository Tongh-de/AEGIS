const CONFIG = {
    CANVAS_WIDTH: 800,
    CANVAS_HEIGHT: 500,
    
    HOOK: {
        BASE_SPEED: 5,
        RETRACT_SPEED: 3,
        SWING_SPEED: 0.02,
        BASE_LENGTH: 30,
        MAX_LENGTH: 400
    },

    GAME: {
        BASE_TIME: 60,
        LEVEL_BASE_TARGET: 500,
        LEVEL_TARGET_MULTIPLIER: 1.5
    },

    ITEMS: {
        PRICES: {
            strength: 100,
            lucky: 150,
            dynamite: 80,
            clock: 120
        }
    }
};

const ITEM_TYPES = {
    goldSmall: { value: 50, weight: 1, radius: 15, color: '#FFD700', emoji: '🟡' },
    goldMedium: { value: 100, weight: 2, radius: 20, color: '#FFD700', emoji: '🟠' },
    goldLarge: { value: 250, weight: 3, radius: 25, color: '#FFD700', emoji: '🔶' },
    rockSmall: { value: 10, weight: 3, radius: 15, color: '#808080', emoji: '🪨' },
    rockMedium: { value: 20, weight: 5, radius: 20, color: '#808080', emoji: '🪨' },
    rockLarge: { value: 30, weight: 7, radius: 25, color: '#808080', emoji: '🪨' },
    diamondSmall: { value: 300, weight: 0.5, radius: 10, color: '#00FFFF', emoji: '💎' },
    diamondLarge: { value: 600, weight: 1, radius: 15, color: '#00FFFF', emoji: '💎' },
    bag: { value: 'random', weight: 2, radius: 18, color: '#8B4513', emoji: '🎁' },
    dynamite: { value: 0, weight: 2, radius: 20, color: '#DC143C', emoji: '🧨', type: 'explosive' },
    pig: { value: 150, weight: 2, radius: 20, color: '#FFB6C1', emoji: '🐷', type: 'moving' },
    diamondPig: { value: 800, weight: 3, radius: 25, color: '#E6E6FA', emoji: '🐷💎', type: 'diamond_pig' }
};
