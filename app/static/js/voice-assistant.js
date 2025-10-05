/**
 * Voice-Activated Learning Assistant
 * Hands-free interaction with the learning platform
 */

class VoiceAssistant {
    constructor() {
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.isListening = false;
        this.isEnabled = false;
        this.commands = this.initializeCommands();
        
        this.initializeSpeechRecognition();
        this.createVoiceUI();
    }
    
    initializeSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            
            this.recognition.continuous = true;
            this.recognition.interimResults = true;
            this.recognition.lang = 'en-US';
            
            this.recognition.onstart = () => {
                this.isListening = true;
                this.updateVoiceUI();
                console.log('Voice recognition started');
            };
            
            this.recognition.onend = () => {
                this.isListening = false;
                this.updateVoiceUI();
                if (this.isEnabled) {
                    // Restart recognition if still enabled
                    setTimeout(() => this.startListening(), 1000);
                }
            };
            
            this.recognition.onresult = (event) => {
                this.handleSpeechResult(event);
            };
            
            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.speak('Sorry, I had trouble understanding. Please try again.');
            };
        } else {
            console.warn('Speech recognition not supported in this browser');
        }
    }
    
    initializeCommands() {
        return {
            // Navigation commands
            'go to dashboard': () => window.location.href = '/',
            'open dashboard': () => window.location.href = '/',
            'show graph': () => window.location.href = '/graph',
            'open graph': () => window.location.href = '/graph',
            'show leaderboard': () => window.location.href = '/leaderboard',
            'open leaderboard': () => window.location.href = '/leaderboard',
            
            // Learning commands
            'start learning': () => this.startQuickLesson(),
            'next concept': () => this.nextConcept(),
            'show progress': () => this.showProgress(),
            'my stats': () => this.showStats(),
            
            // AI commands
            'ai help': () => this.getAIHelp(),
            'ai recommendation': () => this.getAIRecommendation(),
            'study tips': () => this.getStudyTips(),
            
            // Graph commands
            'zoom in': () => this.zoomGraph('in'),
            'zoom out': () => this.zoomGraph('out'),
            'reset graph': () => this.resetGraph(),
            'center graph': () => this.centerGraph(),
            
            // Concept-specific commands
            'explain probability': () => this.explainConcept('probability'),
            'explain statistics': () => this.explainConcept('statistics'),
            'explain random variables': () => this.explainConcept('random_vars'),
            
            // System commands
            'help': () => this.showHelp(),
            'what can you do': () => this.showCapabilities(),
            'stop listening': () => this.disable(),
            'mute': () => this.disable()
        };
    }
    
    createVoiceUI() {
        // Create floating voice assistant button
        const voiceButton = document.createElement('div');
        voiceButton.id = 'voice-assistant-btn';
        voiceButton.className = 'voice-assistant-btn';
        voiceButton.innerHTML = `
            <i class="fas fa-microphone" id="voice-icon"></i>
            <div class="voice-status" id="voice-status">Click to activate</div>
        `;
        
        voiceButton.addEventListener('click', () => this.toggle());
        
        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            .voice-assistant-btn {
                position: fixed;
                bottom: 20px;
                right: 20px;
                width: 60px;
                height: 60px;
                background: linear-gradient(45deg, #007bff, #0056b3);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
                transition: all 0.3s ease;
                z-index: 1000;
            }
            
            .voice-assistant-btn:hover {
                transform: scale(1.1);
                box-shadow: 0 6px 20px rgba(0, 123, 255, 0.4);
            }
            
            .voice-assistant-btn.listening {
                background: linear-gradient(45deg, #dc3545, #c82333);
                animation: pulse 1.5s infinite;
            }
            
            .voice-assistant-btn.disabled {
                background: #6c757d;
                cursor: not-allowed;
            }
            
            .voice-assistant-btn i {
                color: white;
                font-size: 24px;
            }
            
            .voice-status {
                position: absolute;
                bottom: 70px;
                right: 0;
                background: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 8px 12px;
                border-radius: 20px;
                font-size: 12px;
                white-space: nowrap;
                opacity: 0;
                transform: translateY(10px);
                transition: all 0.3s ease;
                pointer-events: none;
            }
            
            .voice-assistant-btn:hover .voice-status {
                opacity: 1;
                transform: translateY(0);
            }
            
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.1); }
                100% { transform: scale(1); }
            }
            
            .voice-transcript {
                position: fixed;
                top: 20px;
                right: 20px;
                background: rgba(0, 0, 0, 0.9);
                color: white;
                padding: 15px;
                border-radius: 10px;
                max-width: 300px;
                z-index: 1001;
                opacity: 0;
                transform: translateX(100%);
                transition: all 0.3s ease;
            }
            
            .voice-transcript.show {
                opacity: 1;
                transform: translateX(0);
            }
        `;
        
        document.head.appendChild(style);
        document.body.appendChild(voiceButton);
        
        // Create transcript display
        const transcript = document.createElement('div');
        transcript.id = 'voice-transcript';
        transcript.className = 'voice-transcript';
        document.body.appendChild(transcript);
    }
    
    toggle() {
        if (!this.recognition) {
            this.speak('Sorry, voice recognition is not supported in your browser.');
            return;
        }
        
        if (this.isEnabled) {
            this.disable();
        } else {
            this.enable();
        }
    }
    
    enable() {
        this.isEnabled = true;
        this.startListening();
        this.speak('Voice assistant activated. How can I help you learn?');
        this.updateVoiceUI();
    }
    
    disable() {
        this.isEnabled = false;
        this.stopListening();
        this.speak('Voice assistant deactivated.');
        this.updateVoiceUI();
    }
    
    startListening() {
        if (this.recognition && this.isEnabled && !this.isListening) {
            try {
                this.recognition.start();
            } catch (error) {
                console.error('Error starting speech recognition:', error);
            }
        }
    }
    
    stopListening() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
        }
    }
    
    updateVoiceUI() {
        const button = document.getElementById('voice-assistant-btn');
        const icon = document.getElementById('voice-icon');
        const status = document.getElementById('voice-status');
        
        if (!button) return;
        
        button.className = 'voice-assistant-btn';
        
        if (!this.recognition) {
            button.classList.add('disabled');
            icon.className = 'fas fa-microphone-slash';
            status.textContent = 'Not supported';
        } else if (this.isListening) {
            button.classList.add('listening');
            icon.className = 'fas fa-microphone';
            status.textContent = 'Listening...';
        } else if (this.isEnabled) {
            icon.className = 'fas fa-microphone';
            status.textContent = 'Ready to listen';
        } else {
            icon.className = 'fas fa-microphone-slash';
            status.textContent = 'Click to activate';
        }
    }
    
    handleSpeechResult(event) {
        let finalTranscript = '';
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript;
            } else {
                interimTranscript += transcript;
            }
        }
        
        // Show transcript
        this.showTranscript(interimTranscript || finalTranscript);
        
        if (finalTranscript) {
            this.processCommand(finalTranscript.toLowerCase().trim());
        }
    }
    
    showTranscript(text) {
        const transcript = document.getElementById('voice-transcript');
        if (transcript) {
            transcript.innerHTML = `
                <div><strong>You said:</strong></div>
                <div>"${text}"</div>
            `;
            transcript.classList.add('show');
            
            // Hide after 3 seconds
            setTimeout(() => {
                transcript.classList.remove('show');
            }, 3000);
        }
    }
    
    processCommand(command) {
        console.log('Processing command:', command);
        
        // Check for exact matches first
        if (this.commands[command]) {
            this.commands[command]();
            return;
        }
        
        // Check for partial matches
        for (const [key, action] of Object.entries(this.commands)) {
            if (command.includes(key) || key.includes(command)) {
                action();
                return;
            }
        }
        
        // If no command found, try to be helpful
        this.handleUnknownCommand(command);
    }
    
    handleUnknownCommand(command) {
        if (command.includes('concept') || command.includes('learn')) {
            this.speak('I can help you learn! Try saying "start learning" or "next concept".');
        } else if (command.includes('help')) {
            this.showHelp();
        } else {
            this.speak('I didn\'t understand that command. Say "help" to see what I can do.');
        }
    }
    
    speak(text) {
        if (this.synthesis) {
            // Cancel any ongoing speech
            this.synthesis.cancel();
            
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 0.9;
            utterance.pitch = 1;
            utterance.volume = 0.8;
            
            // Try to use a pleasant voice
            const voices = this.synthesis.getVoices();
            const preferredVoice = voices.find(voice => 
                voice.name.includes('Google') || 
                voice.name.includes('Microsoft') ||
                voice.lang.startsWith('en')
            );
            
            if (preferredVoice) {
                utterance.voice = preferredVoice;
            }
            
            this.synthesis.speak(utterance);
        }
    }
    
    // Command implementations
    startQuickLesson() {
        this.speak('Starting your next recommended lesson!');
        // Simulate starting a lesson
        setTimeout(() => {
            if (typeof startQuickLesson === 'function') {
                startQuickLesson();
            } else {
                window.location.href = '/course/list';
            }
        }, 1000);
    }
    
    nextConcept() {
        this.speak('Finding your next concept to learn!');
        fetch('/api/adaptive-learning-path')
            .then(response => response.json())
            .then(data => {
                if (data.concepts && data.concepts.length > 0) {
                    const nextConcept = data.concepts[0];
                    this.speak(`Your next concept is ${nextConcept.name}. Opening it now!`);
                    setTimeout(() => {
                        window.location.href = `/course/concept/${nextConcept.id}`;
                    }, 2000);
                } else {
                    this.speak('Great job! You\'ve completed all available concepts.');
                }
            })
            .catch(() => {
                this.speak('Sorry, I couldn\'t find your next concept right now.');
            });
    }
    
    showProgress() {
        this.speak('Let me check your progress!');
        fetch('/api/progress')
            .then(response => response.json())
            .then(data => {
                const message = `You've completed ${data.completed || 0} concepts with ${Math.round(data.percentage || 0)}% overall progress. Keep up the great work!`;
                this.speak(message);
            })
            .catch(() => {
                this.speak('Sorry, I couldn\'t load your progress right now.');
            });
    }
    
    showStats() {
        this.speak('Checking your learning statistics!');
        fetch('/api/user-stats')
            .then(response => response.json())
            .then(data => {
                const message = `You're level ${data.level || 1} with ${data.total_points || 0} experience points. You have a ${data.current_streak || 0} day learning streak!`;
                this.speak(message);
            })
            .catch(() => {
                this.speak('Sorry, I couldn\'t load your stats right now.');
            });
    }
    
    getAIHelp() {
        this.speak('Getting AI recommendations for you!');
        fetch('/api/ai-recommendations')
            .then(response => response.json())
            .then(data => {
                const message = `Based on your ${data.learning_style || 'visual'} learning style, I recommend studying at a ${data.optimal_pace || 'moderate'} pace. Your next optimal study time is ${data.next_study_time || 'now'}!`;
                this.speak(message);
            })
            .catch(() => {
                this.speak('AI recommendations are being prepared. Please try again in a moment.');
            });
    }
    
    getAIRecommendation() {
        this.getAIHelp();
    }
    
    getStudyTips() {
        const tips = [
            'Take regular breaks every 25 minutes using the Pomodoro technique.',
            'Create visual mind maps to connect related concepts.',
            'Practice active recall by explaining concepts out loud.',
            'Use spaced repetition to review concepts at increasing intervals.',
            'Join study groups to learn collaboratively.'
        ];
        
        const randomTip = tips[Math.floor(Math.random() * tips.length)];
        this.speak(`Here's a study tip: ${randomTip}`);
    }
    
    explainConcept(conceptId) {
        this.speak(`Let me explain that concept for you!`);
        // In a real implementation, this would fetch concept explanations
        setTimeout(() => {
            window.location.href = `/course/concept/${conceptId}`;
        }, 1500);
    }
    
    zoomGraph(direction) {
        if (window.location.pathname === '/graph') {
            this.speak(`Zooming ${direction} on the knowledge graph!`);
            // Implement graph zoom functionality
        } else {
            this.speak('Please open the knowledge graph first to use zoom commands.');
        }
    }
    
    resetGraph() {
        if (window.location.pathname === '/graph' && typeof resetGraph === 'function') {
            this.speak('Resetting the knowledge graph view!');
            resetGraph();
        } else {
            this.speak('Please open the knowledge graph to reset the view.');
        }
    }
    
    centerGraph() {
        if (window.location.pathname === '/graph' && typeof centerGraph === 'function') {
            this.speak('Centering the knowledge graph!');
            centerGraph();
        } else {
            this.speak('Please open the knowledge graph to center the view.');
        }
    }
    
    showHelp() {
        const helpMessage = `I can help you navigate and learn! Try saying: "start learning", "show progress", "next concept", "AI help", "show graph", "go to dashboard", or "show leaderboard". Say "what can you do" for more options.`;
        this.speak(helpMessage);
    }
    
    showCapabilities() {
        const capabilities = `I can help you with navigation, learning commands, AI assistance, graph controls, and progress tracking. I can also explain concepts, provide study tips, and give you personalized recommendations. Just speak naturally and I'll do my best to help!`;
        this.speak(capabilities);
    }
}

// Initialize voice assistant when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize on pages where it makes sense
    if (document.body.classList.contains('no-voice')) {
        return;
    }
    
    window.voiceAssistant = new VoiceAssistant();
    
    // Add keyboard shortcut (Ctrl/Cmd + Shift + V)
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'V') {
            e.preventDefault();
            window.voiceAssistant.toggle();
        }
    });
});