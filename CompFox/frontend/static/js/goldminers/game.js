class Game {
    constructor() {
        this.canvas = null;
        this.ctx = null;
        this.isRunning = false;
        this.level = 1;
        this.timeLeft = CONFIG.GAME.BASE_TIME;
        this.totalGold = 0;
        this.levelTarget = 0; // 初始化目标分数
        
        this.players = [
            {
                score: 0,
                hook: new Hook(0, 200, 30),
                items: []
            },
            {
                score: 0,
                hook: new Hook(1, 600, 30),
                items: []
            }
        ];
        
        this.shop = new Shop();
        this.inputHandler = new InputHandler(this);
        
        this.animationId = null;
    }

    startGame() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        
        // 调整 canvas 大小以适应容器
        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());

        document.getElementById('startModal').style.display = 'none';
        this.level = 1;
        this.totalGold = 0;
        
        this.players.forEach((player, index) => {
            player.score = 0;
            player.hook.reset();
        });
        
        this.generateItems();
        this.timeLeft = CONFIG.GAME.BASE_TIME;
        this.isRunning = true;
        this.updateUI();
        this.gameLoop();
    }

    resizeCanvas() {
        const container = this.canvas.parentElement;
        const containerRect = container.getBoundingClientRect();
        
        // 保持 16:10 的宽高比
        const aspectRatio = 16 / 10;
        let newWidth = containerRect.width - 20;
        let newHeight = newWidth / aspectRatio;
        
        if (newHeight > containerRect.height - 20) {
            newHeight = containerRect.height - 20;
            newWidth = newHeight * aspectRatio;
        }
        
        this.canvas.width = newWidth;
        this.canvas.height = newHeight;
        
        // 更新配置
        CONFIG.CANVAS_WIDTH = newWidth;
        CONFIG.CANVAS_HEIGHT = newHeight;
        
        // 重新定位玩家
        this.players[0].hook.x = newWidth * 0.25;
        this.players[1].hook.x = newWidth * 0.75;
    }

    generateItems() {
        // 为两个玩家设置同一个物品列表
        const sharedItems = [];

        const itemCounts = {
            goldSmall: 8 + Math.floor(Math.random() * 4),
            goldMedium: 6 + Math.floor(Math.random() * 4),
            goldLarge: 3 + Math.floor(Math.random() * 3),
            rockSmall: 6 + Math.floor(Math.random() * 4),
            rockMedium: 6 + Math.floor(Math.random() * 4),
            rockLarge: 3 + Math.floor(Math.random() * 3),
            bag: 3 + Math.floor(Math.random() * 3),
            dynamite: 2 + Math.floor(Math.random() * 2),
            pig: 1 + Math.floor(Math.random() * 2),
            diamondPig: Math.floor(Math.random() * 2)
        };

        let hasLucky = this.players.some(p => p.hook.hasLucky);
        if (hasLucky) {
            itemCounts.diamondSmall = 6;
            itemCounts.diamondLarge = 3;
        } else {
            itemCounts.diamondSmall = 1 + Math.floor(Math.random() * 4);
            itemCounts.diamondLarge = Math.floor(Math.random() * 3);
        }

        for (const [type, count] of Object.entries(itemCounts)) {
            for (let i = 0; i < count; i++) {
                const x = 50 + Math.random() * (CONFIG.CANVAS_WIDTH - 100);
                const y = 100 + Math.random() * (CONFIG.CANVAS_HEIGHT - 150);
                const item = new Item(type, x, y);

                let overlapping = true;
                let attempts = 0;
                while (overlapping && attempts < 50) {
                    overlapping = false;
                    for (const existingItem of sharedItems) {
                        const distance = Math.sqrt(
                            Math.pow(item.x - existingItem.x, 2) +
                            Math.pow(item.y - existingItem.y, 2)
                        );
                        if (distance < item.radius + existingItem.radius + 10) {
                            overlapping = true;
                            item.x = 50 + Math.random() * (CONFIG.CANVAS_WIDTH - 100);
                            item.y = 100 + Math.random() * (CONFIG.CANVAS_HEIGHT - 150);
                            break;
                        }
                    }
                    attempts++;
                }

                sharedItems.push(item);
            }
        }

        // 计算当前关卡所有物品的总分
        this.calculateLevelTotal(sharedItems);

        // 两个玩家共享同一个物品列表
        this.players.forEach(player => {
            player.items = sharedItems;
        });
    }

    calculateLevelTotal(items) {
        // 计算所有物品的总分
        let total = 0;
        items.forEach(item => {
            if (item.value === 'random') {
                // 对于随机值物品，取平均值
                total += 175; // (50 + 300) / 2
            } else {
                total += item.value;
            }
        });
        
        // 计算目标分数范围 (35% - 75%)
        const minTarget = Math.floor(total * 0.35);
        const maxTarget = Math.floor(total * 0.75);
        
        // 随机生成目标分数
        this.levelTarget = Math.floor(Math.random() * (maxTarget - minTarget + 1)) + minTarget;
        
        console.log(`Level ${this.level} - Total items value: ${total}, Target: ${this.levelTarget} (${minTarget}-${maxTarget})`);
    }

    gameLoop() {
        if (!this.isRunning) return;

        this.updateGameState();
        this.drawGame();
        this.updateUI();

        if (this.timeLeft <= 0) {
            this.endLevel();
            return;
        }

        this.animationId = requestAnimationFrame(() => this.gameLoop());
    }

    updateGameState() {
        this.timeLeft -= 1/60;

        // 更新物品（移动的小猪）
        if (this.players[0].items) {
            this.players[0].items.forEach(item => {
                item.update();
            });
        }

        this.players.forEach((player, playerIndex) => {
            const score = player.hook.update(player.items, playerIndex * 400);
            if (score > 0) {
                player.score += score;
                this.totalGold += score;
            }
        });

        this.inputHandler.update();
        
        // 更新动画效果
        if (this.animationText) {
            this.animationText.opacity -= 0.01;
            if (this.animationText.opacity <= 0) {
                this.animationText = null;
            }
        }
    }

    drawGame() {
        this.ctx.clearRect(0, 0, CONFIG.CANVAS_WIDTH, CONFIG.CANVAS_HEIGHT);

        // 绘制两个玩家的游戏（在同一区域）
        this.drawPlayerGame(this.players[0], 0);
        this.drawPlayerGame(this.players[1], 0);
        
        // 绘制动画文本
        if (this.animationText) {
            this.ctx.globalAlpha = this.animationText.opacity;
            this.ctx.fillStyle = this.animationText.color;
            this.ctx.font = this.animationText.font;
            this.ctx.textAlign = 'center';
            this.ctx.fillText(
                this.animationText.text,
                this.animationText.x,
                this.animationText.y
            );
            this.ctx.globalAlpha = 1;
        }
    }

    drawPlayerGame(player, offsetX) {
        // 绘制矿工
        this.ctx.font = '35px Arial';
        this.ctx.fillText('👷', player.hook.x - 15 + offsetX, 45);

        player.hook.draw(this.ctx, offsetX);

        player.items.forEach(item => {
            item.draw(this.ctx, offsetX);
        });

        const statusOffset = 10 + offsetX;
        if (player.hook.hasStrength) {
            this.ctx.fillStyle = '#FF6B6B';
            this.ctx.font = '14px Arial';
            this.ctx.fillText('💪 力量增强', statusOffset, 490);
        }
        if (player.hook.hasLucky) {
            this.ctx.fillStyle = '#4ECDC4';
            this.ctx.font = '14px Arial';
            this.ctx.fillText('🍀 幸运提升', statusOffset, 15);
        }
        if (this.shop.getItemCount('dynamite') > 0) {
            this.ctx.fillStyle = '#FFD93D';
            this.ctx.font = '14px Arial';
            this.ctx.fillText(`💣 x${this.shop.getItemCount('dynamite')}`, statusOffset + 280, 490);
        }
        if (this.shop.getItemCount('clock') > 0) {
            this.ctx.fillStyle = '#6BCB77';
            this.ctx.font = '14px Arial';
            this.ctx.fillText(`⏰ x${this.shop.getItemCount('clock')}`, statusOffset + 280, 15);
        }
    }

    updateUI() {
        document.getElementById('player1Score').textContent = this.players[0].score;
        document.getElementById('player2Score').textContent = this.players[1].score;
        document.getElementById('currentLevel').textContent = this.level;
        document.getElementById('timeLeft').textContent = Math.max(0, Math.floor(this.timeLeft));

        const totalScore = this.players[0].score + this.players[1].score;

        document.getElementById('totalTarget').textContent = this.levelTarget || 0;
        document.getElementById('totalScore').textContent = totalScore;
        document.getElementById('totalGold').textContent = this.totalGold;

        const itemTypes = ['strength', 'lucky', 'dynamite', 'clock'];
        itemTypes.forEach(type => {
            document.getElementById(`shared-${type}`).textContent = this.shop.getItemCount(type);
            document.getElementById(`shared-${type}2`).textContent = this.shop.getItemCount(type);
        });
    }

    endLevel() {
        this.isRunning = false;
        
        const totalScore = this.players[0].score + this.players[1].score;

        if (totalScore >= this.levelTarget) {
            this.showShop();
        } else {
            this.showGameOver();
        }
    }

    showShop() {
        document.getElementById('shopTotalGold').textContent = this.totalGold;

        const itemTypes = ['strength', 'lucky', 'dynamite', 'clock'];
        itemTypes.forEach(type => {
            document.getElementById(`shop-${type}`).textContent = this.shop.getItemCount(type);
        });

        document.getElementById('shopModal').style.display = 'flex';
    }

    buyItem(itemType) {
        const result = this.shop.buyItem(itemType, this.totalGold);
        if (result.success) {
            this.totalGold = result.remainingGold;
            document.getElementById('shopTotalGold').textContent = this.totalGold;
            document.getElementById(`shop-${itemType}`).textContent = result.newAmount;
            this.showAnimationText(`购买成功！价格: ${result.price}`, '#4ECDC4', '20px Arial');
        } else {
            this.showAnimationText(`价格: ${result.price} 金币不足`, '#FF6B6B', '20px Arial');
        }
    }

    useItem(playerIndex, itemType) {
        if (!this.isRunning) return;

        const player = this.players[playerIndex];
        const hook = player.hook;

        if (itemType === 'strength' && this.shop.useItem('strength')) {
            hook.hasStrength = true;
        }

        if (itemType === 'lucky' && this.shop.useItem('lucky')) {
            hook.hasLucky = true;
        }

        if (itemType === 'dynamite' && this.shop.useItem('dynamite') && hook.caughtItem) {
            hook.caughtItem = null;
            hook.length = CONFIG.HOOK.BASE_LENGTH;
            hook.state = 'idle';
        }

        if (itemType === 'clock' && this.shop.useItem('clock') && hook.state === 'idle') {
            this.timeLeft += 10;
        }
    }

    triggerHook(playerIndex) {
        if (!this.isRunning) return;
        this.players[playerIndex].hook.launch();
    }

    nextLevel() {
        document.getElementById('shopModal').style.display = 'none';
        this.level++;
        this.timeLeft = CONFIG.GAME.BASE_TIME;

        this.players.forEach(player => {
            player.hook.reset();
        });

        if (this.shop.getItemCount('clock') > 0) {
            this.timeLeft += this.shop.getItemCount('clock') * 10;
            for (let i = 0; i < this.shop.getItemCount('clock'); i++) {
                this.shop.useItem('clock');
            }
        }

        this.generateItems();

        this.isRunning = true;
        this.updateUI();
        this.gameLoop();
    }

    showGameOver() {
        document.getElementById('finalScore1').textContent = this.players[0].score;
        document.getElementById('finalScore2').textContent = this.players[1].score;
        document.getElementById('finalTotalScore').textContent = 
            this.players[0].score + this.players[1].score;
        document.getElementById('gameOverModal').style.display = 'flex';
    }

    showAnimationText(text, color = '#FFD700', font = '30px Arial') {
        this.animationText = {
            text: text,
            color: color,
            font: font,
            x: CONFIG.CANVAS_WIDTH / 2,
            y: CONFIG.CANVAS_HEIGHT / 2,
            opacity: 1
        };
    }

    restartGame() {
        document.getElementById('gameOverModal').style.display = 'none';
        document.getElementById('shopModal').style.display = 'none';

        this.shop.reset();
        this.startGame();
    }
}
