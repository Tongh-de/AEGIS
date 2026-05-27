class Hook {
    constructor(playerIndex, x, y) {
        this.playerIndex = playerIndex;
        this.x = x;
        this.y = y;
        this.angle = 0;
        this.length = CONFIG.HOOK.BASE_LENGTH;
        this.state = 'idle'; // idle, extending, retracting
        this.swingDirection = 1;
        this.speed = CONFIG.HOOK.BASE_SPEED;
        this.caughtItem = null;
        this.hasStrength = false;
        this.hasLucky = false;
    }

    update(items, offsetX) {
        switch (this.state) {
            case 'idle':
                this.angle += this.swingDirection * CONFIG.HOOK.SWING_SPEED;
                if (this.angle > Math.PI / 2.5 || this.angle < -Math.PI / 2.5) {
                    this.swingDirection *= -1;
                }
                break;
            
            case 'extending':
                this.length += this.speed;
                
                const hookEndX = this.x + Math.sin(this.angle) * this.length;
                const hookEndY = this.y + Math.cos(this.angle) * this.length;

                if (hookEndX < 10 || hookEndX > CONFIG.CANVAS_WIDTH - 10 || hookEndY > CONFIG.CANVAS_HEIGHT) {
                    this.state = 'retracting';
                    return 0;
                }

                for (let i = items.length - 1; i >= 0; i--) {
                    const item = items[i];
                    const distance = Math.sqrt(
                        Math.pow(hookEndX - item.x, 2) +
                        Math.pow(hookEndY - item.y, 2)
                    );

                    if (distance < item.radius + 5) {
                        // 处理特殊物品
                        if (item.type === 'explosive') {
                            // 炸药桶爆炸
                            if (item.explode()) {
                                // 炸掉附近的物品
                                for (let j = items.length - 1; j >= 0; j--) {
                                    const otherItem = items[j];
                                    const explosionDistance = Math.sqrt(
                                        Math.pow(item.x - otherItem.x, 2) +
                                        Math.pow(item.y - otherItem.y, 2)
                                    );
                                    if (explosionDistance < item.explosionRadius) {
                                        items.splice(j, 1);
                                    }
                                }
                            }
                            this.state = 'retracting';
                            return 0;
                        } else if (item.type === 'diamond_pig') {
                            // 钻石小猪闪避
                            if (item.dodge()) {
                                // 小猪闪避，钩子继续延伸
                                continue;
                            } else {
                                // 已经闪避过，被抓住
                                this.caughtItem = item;
                                items.splice(i, 1);
                                this.state = 'retracting';
                                return item.value;
                            }
                        } else {
                            // 普通物品
                            this.caughtItem = item;
                            items.splice(i, 1);
                            this.state = 'retracting';
                            return 0;
                        }
                    }
                }
                break;
            
            case 'retracting':
                const retractSpeed = this.caughtItem ? 
                    this.speed / (this.caughtItem.weight / (this.hasStrength ? 2 : 1)) : 
                    this.speed;
                
                this.length -= retractSpeed;

                if (this.length <= CONFIG.HOOK.BASE_LENGTH) {
                    this.length = CONFIG.HOOK.BASE_LENGTH;
                    this.state = 'idle';

                    if (this.caughtItem) {
                        let value = this.caughtItem.value;
                        if (value === 'random') {
                            // 礼盒逻辑：有机会获得随机分数或道具
                            const random = Math.random();
                            if (random < 0.7) {
                                // 70% 概率获得随机分数（不超过两个钻石的总分）
                                const maxScore = 600 * 2; // 两个大钻石的总分
                                value = Math.floor(Math.random() * maxScore) + 50;
                            } else {
                                // 30% 概率获得道具
                                const availableItems = ['strength', 'lucky', 'dynamite', 'clock'];
                                const randomItem = availableItems[Math.floor(Math.random() * availableItems.length)];
                                
                                // 通知游戏实例添加道具并显示动画
                                if (window.gameInstance) {
                                    window.gameInstance.shop.items[randomItem] = (window.gameInstance.shop.items[randomItem] || 0) + 1;
                                    window.gameInstance.showAnimationText(`获得道具: ${randomItem === 'strength' ? '力量' : randomItem === 'lucky' ? '幸运草' : randomItem === 'dynamite' ? '炸药' : '时钟'}`, '#4ECDC4', '24px Arial');
                                }
                                value = 0;
                            }
                        } else if ((value === 300 || value === 600) && this.hasLucky) {
                            // 幸运草效果：增加钻石价值50%
                            value = Math.floor(value * 1.5);
                            if (window.gameInstance) {
                                window.gameInstance.showAnimationText('幸运草生效！钻石价值+50%', '#FFD93D', '20px Arial');
                            }
                        }
                        const score = value;
                        this.caughtItem = null;
                        this.hasStrength = false;
                        this.hasLucky = false;
                        return score;
                    }
                }
                break;
        }
        return 0;
    }

    draw(ctx, offsetX) {
        const hookEndX = this.x + Math.sin(this.angle) * this.length + offsetX;
        const hookEndY = this.y + Math.cos(this.angle) * this.length;

        ctx.strokeStyle = '#8B4513';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(this.x + offsetX, this.y);
        ctx.lineTo(hookEndX, hookEndY);
        ctx.stroke();

        ctx.font = '25px Arial';
        ctx.fillText('🪝', hookEndX - 12, hookEndY + 12);

        if (this.caughtItem) {
            ctx.font = `${this.caughtItem.radius * 2.2}px Arial`;
            ctx.fillText(this.caughtItem.emoji, hookEndX - this.caughtItem.radius, hookEndY + this.caughtItem.radius);
        }
    }

    launch() {
        if (this.state === 'idle') {
            this.state = 'extending';
        }
    }

    reset() {
        this.angle = 0;
        this.length = CONFIG.HOOK.BASE_LENGTH;
        this.state = 'idle';
        this.caughtItem = null;
        this.hasStrength = false;
        this.hasLucky = false;
    }
}

class Item {
    constructor(type, x, y) {
        this.type = type;
        this.x = x;
        this.y = y;
        this.config = ITEM_TYPES[type];
        this.value = this.config.value;
        this.weight = this.config.weight;
        this.radius = this.config.radius;
        this.color = this.config.color;
        this.emoji = this.config.emoji;
        this.type = this.config.type || 'normal';
        
        // 特殊物品属性
        if (this.type === 'moving' || this.type === 'diamond_pig') {
            this.direction = Math.random() > 0.5 ? 1 : -1;
            this.speed = 1 + Math.random() * 1.5;
            this.isMoving = true;
            this.dodged = false; // 钻石小猪是否已经闪避过
        }
        
        // 爆炸效果
        if (this.type === 'explosive') {
            this.exploded = false;
            this.explosionRadius = 150;
            this.explosionTimer = 0;
        }
    }

    update() {
        // 移动的物品（小猪）
        if (this.type === 'moving' || this.type === 'diamond_pig') {
            this.x += this.speed * this.direction;
            
            // 边界检测
            if (this.x < this.radius) {
                this.x = this.radius;
                this.direction = 1;
            } else if (this.x > (CONFIG.CANVAS_WIDTH || 800) - this.radius) {
                this.x = (CONFIG.CANVAS_WIDTH || 800) - this.radius;
                this.direction = -1;
            }
        }
        
        // 爆炸效果
        if (this.exploded) {
            this.explosionTimer++;
        }
    }

    draw(ctx, offsetX) {
        if (this.type === 'diamond_pig') {
            // 绘制钻石小猪，钻石在小猪上方
            const pigSize = this.radius * 2.2;
            const diamondSize = this.radius * 1.5;
            
            ctx.font = `${pigSize}px Arial`;
            // 先绘制小猪
            ctx.fillText('🐷', this.x - this.radius + offsetX, this.y + this.radius);
            
            // 再绘制钻石在小猪上方，位置更偏上以形成重叠效果
            ctx.font = `${diamondSize}px Arial`;
            const diamondY = this.y - this.radius * 0.8;
            ctx.fillText('💎', this.x - this.radius + offsetX, diamondY);
        } else {
            ctx.font = `${this.radius * 2.2}px Arial`;
            ctx.fillText(this.emoji, this.x - this.radius + offsetX, this.y + this.radius);
        }
        
        // 绘制爆炸效果
        if (this.exploded) {
            const alpha = 1 - (this.explosionTimer / 30);
            if (alpha > 0) {
                ctx.globalAlpha = alpha;
                ctx.fillStyle = '#FF4500';
                ctx.beginPath();
                ctx.arc(this.x + offsetX, this.y, this.explosionRadius * (this.explosionTimer / 30), 0, Math.PI * 2);
                ctx.fill();
                ctx.globalAlpha = 1;
            }
        }
    }

    explode() {
        if (this.type === 'explosive' && !this.exploded) {
            this.exploded = true;
            return true;
        }
        return false;
    }

    dodge() {
        if (this.type === 'diamond_pig' && !this.dodged) {
            this.dodged = true;
            this.speed *= 3;
            this.direction *= -1;
            return true;
        }
        return false;
    }
}
