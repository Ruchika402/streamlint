import { BrowserRouter, Routes, Route } from 'react-router-dom';
import SessionPage from './pages/SessionPage';
import SeoPage from './pages/SeoPage';
import { Analytics } from '@vercel/analytics/react';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<SessionPage />} />
        <Route path="/s/:token" element={<SessionPage />} />
        
        <Route path="/python-code-review" element={
          <SeoPage language="Python" title="Free AI Python Code Review" description="Get instant AI-powered code reviews for your Python projects. Find bugs, security issues, and style improvements in seconds." sampleCode={'def divide(a, b):\n    return a / b\n\nprint(divide(10, 0)) # Bug: Division by zero'} />
        } />
        <Route path="/django-code-review" element={
          <SeoPage language="Django" title="Free AI Django Code Review" description="Automated code reviews for Django applications. Catch security vulnerabilities and performance bottlenecks." sampleCode={'from django.http import JsonResponse\n\ndef get_user(request):\n    # Bug: Missing auth check\n    return JsonResponse({\'user\': \'admin\'})'} />
        } />
        <Route path="/javascript-code-review" element={
          <SeoPage language="JavaScript" title="Free AI JavaScript Code Review" description="Real-time AI code reviews for JavaScript and TypeScript. Improve your code quality instantly." sampleCode={'function divide(a, b) {\n  return a / b;\n}\nconsole.log(divide(10, 0)); // Bug: Division by zero'} />
        } />
        <Route path="/java-code-review" element={
          <SeoPage language="Java" title="Free AI Java Code Review" description="Automated Java code reviews. Find NullPointerExceptions, memory leaks, and concurrency bugs." sampleCode={'public class Main {\n  public static void main(String[] args) {\n    int x = 10 / 0; // Bug: Division by zero\n  }\n}'} />
        } />
        <Route path="/c-code-review" element={
          <SeoPage language="C" title="Free AI C Code Review" description="Find memory leaks, segmentation faults, and buffer overflows in your C code." sampleCode={'int main() {\n  int* p = NULL;\n  return *p; // Bug: Null pointer dereference\n}'} />
        } />
        <Route path="/cpp-code-review" element={
          <SeoPage language="C++" title="Free AI C++ Code Review" description="Modern C++ code reviews. Catch memory issues, undefined behavior, and performance bottlenecks." sampleCode={'int main() {\n  int* p = nullptr;\n  return *p; // Bug: Null pointer dereference\n}'} />
        } />
        <Route path="/csharp-code-review" element={
          <SeoPage language="C#" title="Free AI C# Code Review" description="Automated C# and .NET code reviews. Find exceptions and performance issues." sampleCode={'public class Program {\n  public static void Main() {\n    int x = 10 / 0; // Bug: DivideByZeroException\n  }\n}'} />
        } />
        <Route path="/go-code-review" element={
          <SeoPage language="Go" title="Free AI Go Code Review" description="Idiomatic Go code reviews. Find goroutine leaks, race conditions, and error handling issues." sampleCode={'package main\n\nfunc main() {\n  var a int = 10\n  var b int = 0\n  println(a / b) // Bug: Division by zero panic\n}'} />
        } />
        <Route path="/rust-code-review" element={
          <SeoPage language="Rust" title="Free AI Rust Code Review" description="Find unwraps, borrow checker issues, and unsafe blocks in your Rust code." sampleCode={'fn main() {\n  let x: i32 = 10;\n  let y: i32 = 0;\n  println!("{}", x / y); // Bug: Panic on division by zero\n}'} />
        } />
        <Route path="/ruby-code-review" element={
          <SeoPage language="Ruby" title="Free AI Ruby Code Review" description="Automated Ruby code reviews. Find N+1 queries, nil errors, and security issues." sampleCode={'def divide(a, b)\n  a / b\nend\n\nputs divide(10, 0) # Bug: ZeroDivisionError'} />
        } />
        <Route path="/php-code-review" element={
          <SeoPage language="PHP" title="Free AI PHP Code Review" description="Find SQL injection, XSS, and type errors in your PHP code." sampleCode={'<?php\nfunction divide($a, $b) {\n  return $a / $b;\n}\necho divide(10, 0); // Bug: Division by zero warning\n?>'} />
        } />
        <Route path="/html-code-review" element={
          <SeoPage language="HTML" title="Free AI HTML Code Review" description="Check your HTML for accessibility issues, missing tags, and semantic errors." sampleCode={'<div>\n  <p>Hello World</p>\n</div> <!-- Missing lang attribute and semantic HTML -->'} />
        } />
        <Route path="/swift-code-review" element={
          <SeoPage language="Swift" title="Free AI Swift Code Review" description="Find force unwraps, memory leaks, and concurrency issues in iOS and macOS code." sampleCode={'let x: Int = 10\nlet y: Int = 0\nlet z = x / y // Bug: Division by zero crash'} />
        } />
        <Route path="/r-code-review" element={
          <SeoPage language="R" title="Free AI R Code Review" description="Statistical code reviews for R. Find vectorization issues and data type mismatches." sampleCode={'x <- c(1, 2, 3)\ny <- mean(x)\nprint(y) # Suggestion: check for missing values (NA)'} />
        } />
        <Route path="/sql-code-review" element={
          <SeoPage language="SQL" title="Free AI SQL Code Review" description="Find SQL injection risks, missing indexes, and inefficient queries." sampleCode={'SELECT * FROM users WHERE id = " + user_input + "; -- Bug: SQL Injection'} />
        } />
      </Routes>
      <Analytics />
    </BrowserRouter>
  );
}

export default App;