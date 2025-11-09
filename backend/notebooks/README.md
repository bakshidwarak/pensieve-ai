# 🤖 Agent Performance Analysis Notebooks

This directory contains Jupyter notebooks for comprehensive testing and analysis of the Pensieve AI agent systems.

## 📁 Notebooks

### `agent_performance_analysis.ipynb`
**Comprehensive Performance Testing & SDG Analysis**

A complete testing framework that includes:

- **Performance Metrics Collection** - Response time, memory usage, CPU utilization
- **Comparative Testing** - Side-by-side comparison of all agent systems
- **Load Testing** - Concurrent request handling and stress testing
- **SDG Analysis** - System Design & Governance evaluation
- **Visualization** - Charts and graphs for performance analysis
- **Report Generation** - Automated performance and SDG reports

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   cd backend/notebooks
   pip install -r requirements.txt
   ```

2. **Start Jupyter Notebook**
   ```bash
   jupyter notebook
   ```

3. **Open the Analysis Notebook**
   - Navigate to `agent_performance_analysis.ipynb`
   - Run all cells to perform comprehensive testing

## 🎯 Testing Capabilities

### Performance Testing
- **Response Time Analysis** - Average, median, 95th percentile
- **Memory Usage Tracking** - Peak and average memory consumption
- **CPU Utilization** - Resource usage monitoring
- **Throughput Measurement** - Queries per second
- **Success Rate Analysis** - Error rate and reliability metrics

### Load Testing
- **Concurrent Request Testing** - Multiple simultaneous queries
- **Stress Testing** - High-volume query processing
- **Resource Scaling** - Memory and CPU under load
- **Performance Degradation** - Response time under stress

### SDG (System Design & Governance) Analysis
- **Reliability Metrics** - Availability, error rates, consistency
- **Scalability Analysis** - Throughput, resource efficiency
- **Maintainability Assessment** - Code complexity, error handling
- **Security & Compliance** - Best practices evaluation
- **Monitoring & Observability** - Logging and alerting recommendations

## 📊 Generated Reports

The notebook automatically generates:

1. **Performance Report** (`performance_report_YYYYMMDD_HHMMSS.md`)
   - Detailed performance metrics
   - Agent comparison tables
   - Optimization recommendations

2. **SDG Analysis Report** (`sdg_analysis_YYYYMMDD_HHMMSS.md`)
   - System design evaluation
   - Governance recommendations
   - Security and compliance guidelines

3. **CSV Data Export** (`test_results_YYYYMMDD_HHMMSS.csv`)
   - Raw test data for further analysis
   - Query-by-query performance metrics
   - Error logs and debugging information

## 🔧 Configuration

### Environment Variables
```bash
export OPENAI_API_KEY="your-openai-api-key"
export QDRANT_URL="http://localhost:6333"
export SERP_API_KEY="your-serp-api-key"  # Optional
```

### Test Configuration
Modify the `TestConfig` class in the notebook to adjust:
- Maximum concurrent requests
- Test timeout settings
- Sample size for testing
- Performance thresholds

## 📈 Visualization

The notebook includes comprehensive visualizations:

- **Response Time Comparison** - Bar charts comparing agent performance
- **Success Rate Analysis** - Reliability metrics visualization
- **Memory Usage Tracking** - Resource consumption over time
- **Load Test Results** - Performance under concurrent load
- **Performance Score** - Combined metric for overall assessment

## 🎯 Use Cases

### Development Testing
- Compare different agent implementations
- Identify performance bottlenecks
- Validate optimizations
- Debug error patterns

### Production Monitoring
- Establish baseline performance metrics
- Set up alerting thresholds
- Monitor system health
- Track performance trends

### SDG Compliance
- Evaluate system design quality
- Assess governance practices
- Identify security gaps
- Plan infrastructure improvements

## 🚀 Advanced Usage

### Custom Test Queries
```python
# Add custom test queries
custom_queries = [
    {"query": "Your custom query", "category": "custom", "context": "Test context"}
]
test_queries.extend(custom_queries)
```

### Load Testing Configuration
```python
# Adjust load test parameters
config.max_concurrent_requests = 20
config.sample_size = 200
```

### Custom Metrics
```python
# Add custom performance metrics
def custom_metric_calculator(results):
    # Your custom analysis logic
    return custom_metrics
```

## 📝 Best Practices

1. **Run Tests Regularly** - Schedule automated performance testing
2. **Monitor Trends** - Track performance over time
3. **Set Baselines** - Establish performance benchmarks
4. **Document Changes** - Keep track of optimizations
5. **Review Reports** - Act on performance recommendations

## 🛠️ Troubleshooting

### Common Issues

1. **Import Errors** - Ensure all dependencies are installed
2. **API Key Issues** - Verify environment variables are set
3. **Memory Issues** - Reduce sample size for large tests
4. **Timeout Errors** - Increase test timeout settings

### Debug Mode
```python
# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 Additional Resources

- [Performance Testing Guide](../docs/performance-testing.md)
- [SDG Best Practices](../docs/sdg-guidelines.md)
- [Agent Architecture](../docs/agent-architecture.md)
- [Monitoring Setup](../docs/monitoring-setup.md)

