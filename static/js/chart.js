function renderChart(meals) {
  if (!meals || meals.length === 0) return;

  const calories = meals.map(m => m.calories);

  new Chart(document.getElementById("chart"), {
    type: "bar",
    data: {
      labels: meals.map((_, i) => "Meal " + (i + 1)),
      datasets: [{
        label: "Calories",
        data: calories
      }]
    }
  });
}