<h1>Amazon Clone</h1>
    
<h2>Technologies</h2>
<p>React + TypeScript + Django REST Framework + PostgreSQL + Celery + RabbitMQ</p>

<h2>Running</h2>
<p>In the root folder:</p>

  <code>docker-compose up</code></li>
  <p>If the backend localhost is not working, try reloading the backend service. This is a common issue caused by the backend server starting before the message broker has finished.
  </p>

  <code>docker-compose restart backend</code>

  <span>The backend server is available on port 8000.</span>
  <span>The frontend server is available on port 3000.</span>


<h2>Services</h2>
  <ul>
    <li>frontend</li>
    <li>backend</li>
    <li>database - included in the volume is a sample database with a small amount of data for functionality testing. It's worth reviewing what might be provided there</li>
    <li>celery worker</li>
    <li>celery beat</li>
    <li>message broker - rabbitmq</li>
    <li>stripe cli - gateway for payments</li>
    <li>database and rabbitmq service controlling starting of backend service</li>
  </ul>


<h2>Features</h2>
<ul>
  <li>Registration</li>
  <li>Login/Logout</li>
  <li>Product Filtering</li>
  <li>Ability to Purchase Products</li>
  <li>Shopping Cart</li>
  <li>Order Preview and Ability to Rate Ordered Products</li>
  <li>Currency Change</li>
  <li>Background Task in the Form of an API That Once, and Then at Specified Intervals in settings.py Using Celery, Updates Currency Exchange Rates</li>
  <li>User Data Editing</li>
  <li>Recommendations</li>
  <li>Review System</li>
  <li>Payment System with Stripe Payment and Webhooks Controlling Operations on the Database</li>
  <li>Unit tests for some functionalities</li>
</ul>



<h2>Public API</h2>
<ul>
  <li>
    <span>Currency Exchange API</span>
    <a href="https://fixer.io/documentation">here</a>
  </li>
  
  <li>
    <span>Payment Gateway</span>
    <a href="https://stripe.com/docs/checkout/quickstart">here</a>
  </li>
</ul>





