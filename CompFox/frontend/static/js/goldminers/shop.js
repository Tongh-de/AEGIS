class Shop {
    constructor() {
        this.items = {
            strength: 0,
            lucky: 0,
            dynamite: 0,
            clock: 0
        };
    }

    buyItem(itemType, totalGold) {
        // 价格随机波动：50% - 350%
        const basePrice = CONFIG.ITEMS.PRICES[itemType];
        const fluctuation = 0.5 + Math.random() * 3; // 0.5 到 3.5
        const price = Math.floor(basePrice * fluctuation);
        
        if (totalGold >= price) {
            this.items[itemType]++;
            return { success: true, newAmount: this.items[itemType], remainingGold: totalGold - price, price: price };
        }
        return { success: false, message: '金币不足', price: price };
    }

    useItem(itemType) {
        if (this.items[itemType] > 0) {
            this.items[itemType]--;
            return true;
        }
        return false;
    }

    getItemCount(itemType) {
        return this.items[itemType] || 0;
    }

    reset() {
        this.items = {
            strength: 0,
            lucky: 0,
            dynamite: 0,
            clock: 0
        };
    }

    getTotalItems() {
        return Object.values(this.items).reduce((total, count) => total + count, 0);
    }
}
