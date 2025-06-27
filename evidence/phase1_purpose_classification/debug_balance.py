from purpose_classifier import PurposeClassifier

classifier = PurposeClassifier()

# Test the bias test theory
bias_test_theory = """This theory involves causal relationships that cause significant effects through
causal mechanisms. The causal processes lead to outcomes that result from causal
influences. These causal effects are caused by systematic causal factors that
cause changes in the dependent variables through causal pathways."""

result = classifier.classify_theory_purposes(bias_test_theory)
print('Purpose Confidence Scores:')
for purpose, conf in result['purpose_confidence'].items():
    print(f'  {purpose}: {conf:.3f}')

print(f'\nCausal score: {result["purpose_confidence"]["causal"]:.3f}')
other_scores = [v for k, v in result['purpose_confidence'].items() if k != 'causal']
avg_other = sum(other_scores) / len(other_scores)
print(f'Average other scores: {avg_other:.3f}')
print(f'Ratio: {result["purpose_confidence"]["causal"] / avg_other:.2f}')
print(f'Threshold: 2.0')
print(f'Over-emphasis detected: {result["balanced_analysis"]["causal_overemphasis_detected"]}')