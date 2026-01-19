/*
抖音视频上传自动化脚本
在浏览器控制台中执行

使用方法:
  1. 在已登录的抖音创作者中心页面打开开发者工具 (F12)
  2. 切换到 Console 标签
  3. 粘贴此脚本并按 Enter
  4. 按照提示操作
*/

class DouyinUploaderJS {
    constructor() {
        this.videoPath = "";
        this.title = "";
        this.description = "";
        this.topics = [];
    }

    // 等待元素加载
    waitForElement(selector, timeout = 10000) {
        return new Promise((resolve, reject) => {
            if (document.querySelector(selector)) {
                return resolve(document.querySelector(selector));
            }

            const observer = new MutationObserver(() => {
                if (document.querySelector(selector)) {
                    observer.disconnect();
                    resolve(document.querySelector(selector));
                }
            });

            observer.observe(document.body, {
                childList: true,
                subtree: true
            });

            setTimeout(() => {
                observer.disconnect();
                reject(new Error(`Timeout waiting for element: ${selector}`));
            }, timeout);
        });
    }

    // 查找文件输入框
    findFileInput() {
        const selectors = [
            'input[type="file"]',
            'input[accept*="video"]',
            '.upload-input',
            '[class*="upload"] input[type="file"]'
        ];

        for (let selector of selectors) {
            const input = document.querySelector(selector);
            if (input) {
                console.log(`✅ 找到文件输入框: ${selector}`);
                return input;
            }
        }

        console.error('❌ 未找到文件输入框');
        return null;
    }

    // 查找标题输入框
    findTitleInput() {
        const selectors = [
            'input[placeholder*="标题"]',
            'textarea[placeholder*="标题"]',
            'input[maxlength*="30"]',
            '[class*="title"] input',
            '[class*="title"] textarea'
        ];

        for (let selector of selectors) {
            const input = document.querySelector(selector);
            if (input) {
                console.log(`✅ 找到标题输入框: ${selector}`);
                return input;
            }
        }

        console.error('❌ 未找到标题输入框');
        return null;
    }

    // 查找发布按钮
    findPublishButton() {
        const selectors = [
            'button:has-text("发布")',
            'button:has-text("确认")',
            '[class*="publish"] button',
            '.publish-btn',
            'button[type="submit"]'
        ];

        for (let selector of selectors) {
            const button = document.querySelector(selector);
            if (button && button.offsetParent !== null) {
                console.log(`✅ 找到发布按钮: ${selector}`);
                return button;
            }
        }

        console.error('❌ 未找到发布按钮');
        return null;
    }

    // 设置文件
    async setFile(input, filePath) {
        try {
            // 注意：由于浏览器安全限制，无法直接设置本地文件路径
            // 需要用户手动选择文件
            
            console.log('📁 请在打开的文件选择器中选择视频文件');
            console.log(`   文件路径: ${filePath}`);
            
            // 触发点击打开文件选择器
            input.click();
            
            // 提示用户
            alert(`请在文件选择器中选择文件:\n${filePath}`);
            
            return true;
        } catch (error) {
            console.error('❌ 设置文件失败:', error);
            return false;
        }
    }

    // 填写标题
    async fillTitle(titleInput, title) {
        try {
            titleInput.focus();
            titleInput.select();
            document.execCommand('delete', false, null);
            
            // 使用 clipboard 粘贴
            await navigator.clipboard.writeText(title);
            document.execCommand('paste', false, null);
            
            console.log(`✅ 标题填写完成: ${title}`);
            return true;
        } catch (error) {
            console.error('❌ 填写标题失败:', error);
            return false;
        }
    }

    // 点击按钮
    async clickButton(button) {
        try {
            button.scrollIntoViewIfNeeded();
            await new Promise(resolve => setTimeout(resolve, 500));
            button.click();
            console.log('✅ 点击发布按钮');
            return true;
        } catch (error) {
            console.error('❌ 点击按钮失败:', error);
            return false;
        }
    }

    // 主流程
    async upload(config) {
        const { videoPath, title, description, topics } = config;

        console.log('='.repeat(50));
        console.log('🎬 抖音视频上传自动化');
        console.log('='.repeat(50));
        console.log(`📹 视频: ${videoPath}`);
        console.log(`📝 标题: ${title}`);
        if (description) console.log(`📖 描述: ${description}`);
        if (topics) console.log(`🏷️ 话题: ${topics.join(', ')}`);
        console.log('='.repeat(50));

        try {
            // 步骤 1: 查找文件输入框
            console.log('\n📤 步骤 1: 查找上传元素');
            const fileInput = this.findFileInput();
            if (!fileInput) throw new Error('未找到文件输入框');

            // 步骤 2: 设置文件（需要用户手动选择）
            console.log('\n📁 步骤 2: 选择视频文件');
            await this.setFile(fileInput, videoPath);
            
            // 等待用户选择文件
            const confirmed = confirm('文件选择完成后，点击确定继续');
            if (!confirmed) throw new Error('用户取消');

            // 步骤 3: 填写标题
            console.log('\n📝 步骤 3: 填写标题');
            const titleInput = this.findTitleInput();
            if (titleInput) {
                await this.fillTitle(titleInput, title);
            }

            // 步骤 4: 点击发布
            console.log('\n🚀 步骤 4: 点击发布');
            const publishButton = this.findPublishButton();
            if (publishButton) {
                await this.clickButton(publishButton);
            }

            console.log('\n✅ 上传流程完成！');
            console.log('请在浏览器中确认上传状态');

            return true;
        } catch (error) {
            console.error('\n❌ 上传失败:', error.message);
            return false;
        }
    }
}

// 创建实例并运行
const uploader = new DouyinUploaderJS();

// 配置（修改这些值）
const config = {
    videoPath: "/Users/ygh/StudioProjects/Project-Tsukuyomi/src/data/videos/sasuke_specific_1768745166.mp4",
    title: "测试视频",
    description: "使用 JavaScript 自动化上传",
    topics: ["#测试", "#AI视频"]
};

// 运行上传
console.log('准备开始上传...');
setTimeout(() => {
    uploader.upload(config);
}, 1000);
