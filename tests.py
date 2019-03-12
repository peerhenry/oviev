import unittest

if __name__ == '__main__':
  tests = unittest.TestLoader().discover('./tests')
  testRunner = unittest.runner.TextTestRunner()
  result = testRunner.run(tests)
  if not result.wasSuccessful():
      exit(1) 