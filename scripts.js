

/* game script */
const questions = [
  {
      question: "What is the primary benefit of regular exercise?",
      answers: [
          "Improved cardiovascular health",
          "Weight loss",
          "Better flexibility and mobility",
          "Stress relief"
      ],
      correctAnswer: 0
  },
  {
      question: "Which exercise is best for building strength?",
      answers: [
          "Running",
          "Yoga",
          "Weightlifting",
          "Swimming"
      ],
      correctAnswer: 2
  },
  {
      question: "How much water should you drink daily?",
      answers: [
          "1-2 liters",
          "2-3 liters",
          "3-4 liters",
          "4-5 liters"
      ],
      correctAnswer: 1
  },
  {
      question: "What nutrient is essential for muscle repair?",
      answers: [
          "Carbohydrates",
          "Proteins",
          "Fats",
          "Vitamins"
      ],
      correctAnswer: 1
  },


  {
      question: "How many minutes of moderate exercise are recommended per week?",
      answers: [
          "60 minutes",
          "150 minutes",
          "200 minutes",
          "250 minutes"
      ],
      correctAnswer: 1
  },
  
  {
      question: "What is the main benefit of a cool-down routine?",
      answers: [
          "Increase heart rate",
          "Prevent injury",
          "Increase muscle mass",
          "Enhance flexibility"
      ],
      correctAnswer: 1
  },

];

let currentQuestion = 0;
let score = 0;

function displayQuestion() {
  const questionElement = document.getElementById("question");
  const answersElement = document.getElementById("answers");
  const currentQuestionData = questions[currentQuestion];

  questionElement.textContent = currentQuestionData.question;

  answersElement.innerHTML = "";

  currentQuestionData.answers.forEach((answer, index) => {
      const answerButton = document.createElement("button");
      answerButton.textContent = answer;
      answerButton.addEventListener("click", () => {
          if (index === currentQuestionData.correctAnswer) {
              score++;
          }

          currentQuestion++;

          if (currentQuestion < questions.length) {
              displayQuestion();
          } else {
              showResult();
          }
      });

      answersElement.appendChild(answerButton);
  });
}

function showResult() {
  const questionContainer = document.getElementById("question-container");
  const resultContainer = document.getElementById("result");
  const scoreElement = document.getElementById("score");

  questionContainer.style.display = "none";
  resultContainer.style.display = "block";

  scoreElement.textContent = `${score}/${questions.length}`;
}

document.getElementById("restart").addEventListener("click", () => {
  currentQuestion = 0;
  score = 0;
  displayQuestion();

  document.getElementById("question-container").style.display = "block";
  document.getElementById("result").style.display = "none";
});

displayQuestion();

/* game ends */

/* bmi script */

// function calculateBMI(event) {
//     event.preventDefault();
//     const height = document.getElementById('height').value;
//     const weight = document.getElementById('weight').value;
//     if (height > 0 && weight > 0) {
//         const bmi = (weight / ((height / 100) * (height / 100))).toFixed(2);
//         document.getElementById('bmiResult').innerText = `Your BMI is ${bmi}`;
//     } else {
//         document.getElementById('bmiResult').innerText = 'Please enter valid height and weight.';
//     }
// }

document.addEventListener('DOMContentLoaded', () => {
  const slider = document.querySelector('.news-slider');
  const leftArrow = document.querySelector('.left-arrow');
  const rightArrow = document.querySelector('.right-arrow');
  const cards = document.querySelectorAll('.news-card');
  const cardWidth = cards[0].clientWidth + 20; 

  let currentIndex = 0;

  leftArrow.addEventListener('click', () => {
      if (currentIndex > 0) {
          currentIndex--;
      } else {
          currentIndex = cards.length - 1;
      }
      slider.scrollTo({
          left: currentIndex * cardWidth,
          behavior: 'smooth'
      });
  });

  rightArrow.addEventListener('click', () => {
      if (currentIndex < cards.length - 1) {
          currentIndex++;
      } else {
          currentIndex = 0;
      }
      slider.scrollTo({
          left: currentIndex * cardWidth,
          behavior: 'smooth'
      });
  });

  const bmiForm = document.getElementById('bmiForm');
  bmiForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const height = parseFloat(document.getElementById('height').value);
      const weight = parseFloat(document.getElementById('weight').value);

      if (!isNaN(height) && !isNaN(weight) && height > 0 && weight > 0) {
          const bmi = (weight / ((height / 100) ** 2)).toFixed(2);
          let category;

          if (bmi < 18.5) {
              category = 'Underweight';
          } else if (bmi < 24.9) {
              category = 'Normal weight';
          } else if (bmi < 29.9) {
              category = 'Overweight,try some exercises:)';
          } else {
              category = 'Obesity,You should start workout NOW!';
          }

          document.getElementById('bmiResult').innerText = `Your BMI is ${bmi} (${category})`;
      } else {
          document.getElementById('bmiResult').innerText = 'Please enter valid height and weight.';
      }
      
  });
});





/* bmi ends */

document.addEventListener('DOMContentLoaded', function() {
  fetch('/api/programs')
      .then(response => response.json())
      .then(data => {
          const programsContainer = document.getElementById('programs-container');
          programsContainer.innerHTML = '';
          data.forEach(program => {
              const programDiv = document.createElement('div');
              programDiv.classList.add('program');
              programDiv.innerHTML = `
                  <img src="${program.image_url}" alt="${program.name}">
                  <h3>${program.name}</h3>
                  <p>${program.description}</p>
              `;
              programsContainer.appendChild(programDiv);
          });
      })
      .catch(error => console.error('Error fetching programs:', error));
});
