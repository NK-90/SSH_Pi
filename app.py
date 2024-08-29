from flask import Flask, render_template_string, jsonify
import RPi.GPIO as GPIO
import time

app = Flask(__name__)

# GPIO 핀 설정
IN1 = 17
IN2 = 18
IN3 = 27
IN4 = 22

# GPIO 모드 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

# 스텝 시퀀스 설정
step_sequence = [
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1]
]

def set_step(w1, w2, w3, w4):
    GPIO.output(IN1, w1)
    GPIO.output(IN2, w2)
    GPIO.output(IN3, w3)
    GPIO.output(IN4, w4)

def move_motor(steps, direction, delay=0.001):
    if direction == 'forward':
        for i in range(steps):
            for step in step_sequence:
                set_step(*step)
                time.sleep(delay)
    elif direction == 'backward':
        for i in range(steps):
            for step in reversed(step_sequence):
                set_step(*step)
                time.sleep(delay)

@app.route('/')
def index():
    return render_template_string('''
        <h1>모터 제어</h1>
        <button onclick="controlMotor('forward')">전진</button>
        <button onclick="controlMotor('backward')">후진</button>
        <p id="status">모터 상태: 대기 중</p>
        
        <script>
            function controlMotor(direction) {
                fetch('/control/' + direction)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('status').innerText = '모터 상태: ' + data.status;
                });
            }
        </script>
    ''')

@app.route('/control/<direction>')
def control(direction):
    if direction == 'forward':
        move_motor(512, 'forward')
        return jsonify(status="전진 완료")
    elif direction == 'backward':
        move_motor(512, 'backward')
        return jsonify(status="후진 완료")
    else:
        return jsonify(status="잘못된 명령")

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        GPIO.cleanup()