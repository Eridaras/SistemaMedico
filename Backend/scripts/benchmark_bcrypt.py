"""
Benchmark script to determine optimal bcrypt work factor
Run this on your production server to choose appropriate BCRYPT_LOG_ROUNDS
"""
import bcrypt
import time


def benchmark_bcrypt(password='test_password_12345'):
    """Benchmark bcrypt with different work factors"""
    print("=" * 60)
    print("BCRYPT WORK FACTOR BENCHMARK")
    print("=" * 60)
    print(f"Testing password: {password}")
    print(f"Target time: 0.25-0.5 seconds (good UX balance)")
    print("-" * 60)
    
    results = []
    
    for rounds in [10, 11, 12, 13, 14]:
        times = []
        for _ in range(3):  # 3 samples per round
            start = time.time()
            bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds))
            elapsed = time.time() - start
            times.append(elapsed)
        
        avg_time = sum(times) / len(times)
        results.append((rounds, avg_time))
        
        status = "✅ ÓPTIMO" if 0.25 <= avg_time <= 0.5 else (
            "⚠️  RÁPIDO (menos seguro)" if avg_time < 0.25 else "🐌 LENTO (afecta UX)"
        )
        
        print(f"Rounds {rounds:2d}: {avg_time:.3f}s  {status}")
    
    print("-" * 60)
    print("\nRECOMENDACIÓN:")
    
    optimal = [r for r, t in results if 0.25 <= t <= 0.5]
    if optimal:
        recommended = max(optimal)  # Mayor rounds dentro del rango óptimo
        print(f"Usar BCRYPT_LOG_ROUNDS={recommended}")
    else:
        # Si todos están fuera del rango, elegir el más cercano a 0.4s
        recommended = min(results, key=lambda x: abs(x[1] - 0.4))[0]
        print(f"Usar BCRYPT_LOG_ROUNDS={recommended} (compromiso)")
    
    print("\nConfigurar en .env:")
    print(f"BCRYPT_LOG_ROUNDS={recommended}")
    print("=" * 60)
    
    return recommended


if __name__ == '__main__':
    benchmark_bcrypt()
