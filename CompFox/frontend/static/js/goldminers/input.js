class InputHandler {
    constructor(game) {
        this.game = game;
        this.keys = {};
        this.initKeyboard();
    }

    initKeyboard() {
        document.addEventListener('keydown', (event) => {
            if (!this.game.isRunning) return;

            this.keys[event.key] = true;

            // 玩家1: ↓ 或 S 发射钩子, 1-4 使用道具
            if (event.key === 'ArrowDown' || event.key.toLowerCase() === 's') {
                this.game.triggerHook(0);
            } else if (event.key === '1') {
                this.game.useItem(0, 'strength');
            } else if (event.key === '2') {
                this.game.useItem(0, 'lucky');
            } else if (event.key === '3') {
                this.game.useItem(0, 'dynamite');
            } else if (event.key === '4') {
                this.game.useItem(0, 'clock');
            }

            // 玩家2: ↓ 或 K 发射钩子, 小键盘1-4 使用道具
            if (event.key === 'ArrowDown' || event.key.toLowerCase() === 'k') {
                this.game.triggerHook(1);
            } else if (event.key === 'End') {
                this.game.useItem(1, 'strength');
            } else if (event.key === 'ArrowDown' && event.shiftKey) {
                this.game.useItem(1, 'lucky');
            } else if (event.key === 'PageDown') {
                this.game.useItem(1, 'dynamite');
            } else if (event.key === 'ArrowUp' && event.shiftKey) {
                this.game.useItem(1, 'clock');
            }
        });

        document.addEventListener('keyup', (event) => {
            this.keys[event.key] = false;
        });
    }

    update() {
        if (!this.game.isRunning) return;

        // 可以在这里添加持续按键的处理
    }
}
