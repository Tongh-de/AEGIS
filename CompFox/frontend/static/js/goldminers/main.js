let game = null;

document.addEventListener('DOMContentLoaded', function() {
    // 初始化游戏
    game = new Game();
    
    // 确保所有全局函数都可用
    window.game = game;
    window.gameInstance = game; // 用于 Hook 类访问
    window.startGame = function() { game.startGame(); };
    window.triggerHook = function(playerIndex) { game.triggerHook(playerIndex); };
    window.useItem = function(playerIndex, itemType) { game.useItem(playerIndex, itemType); };
    window.buyItem = function(itemType) { game.buyItem(itemType); };
    window.nextLevel = function() { game.nextLevel(); };
    window.restartGame = function() { game.restartGame(); };
});
