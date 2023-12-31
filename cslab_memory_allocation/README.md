# Python Memory Allocation 시간 분석

파이썬 언어에서 메모리 할당량이 높아질수록 프로세스 실행시간이 급격하게 느려지는 현상 관측 및 대안 분석

## 실험 환경

Rocky-Linux 9.2 SSH 서버
CPU : Intel Core i7 - 4790 3.60GHz
RAM : 7.5Gi

### 언어별 동일한 크기의 메모리 할당 시간 비교

1. Python의 메모리 할당 시간 체크

```
y = []
    for i in range(300000000):
     y.append(i)
```
현재 실험 환경에서 append()를 최대 3억번 까지 호출 가능하다는 것을 확인
위 내용을 기준으로 리스트에 3억개의 값을 할당하는 시간을 체크

실행 결과


<img width="365" alt="PYTHON_1" src="https://github.com/AngryOvO/linux_kernel/assets/101005580/c2020d9b-e965-4af6-9374-bcc07c923381">




2. C의 메모리 할당 시간 체크
파이썬의 리스트와 C의 배열이 완전히 동일한 구조가 아니기 때문에 파이썬에서 메모리에 할당한 리스트의 크기를 계산해 그 크기에 근사한 양을 C에서 배열로 할당
대략 인덱스가 6억정도의 정수형 배열을 만들 수 있으며 그에 해당하는 프로세스 실행시간을 체크

실행 결과 (컴파일러의 최적화 옵션을 끈 상태로 실험을 진행)



<img width="259" alt="C_1" src="https://github.com/AngryOvO/linux_kernel/assets/101005580/5df11d6c-ced2-44e9-9896-36b40aa5420a">



3. JAVA의 메모리 할당 시간 체크
JAVA 또한 마찬가지로 진행

실행 결과



<img width="437" alt="JAVA_1" src="https://github.com/AngryOvO/linux_kernel/assets/101005580/7016ab03-4ec3-4f9d-a3dd-48b7a4eb70a6">





## Python의 실행시간 분석

다른 언어에 비해 파이썬으로 작성한 코드의 실행시간이 현저하게 느린 이유에 대한 몇가지 원인들을 찾아보았다.

대표적으로 아래 세 가지를 꼽을 수 있었다.
1. 동적 타입 검사
2. GC (가비지 컬렉션)
3. 인터프리터

각 원인이 파이썬 실행시간에 어떠한 차이를 주는지에 대한 실험을 진행했다.


## 동적 타입 검사 Dynamic type checking

실행시간에 변수나 객체의 타입을 검사하는 기능이다.

Python이 C와 Java와 다른 대표적인 특징 중 하나이다.

파이썬은 명시적으로 타입을 선언하지 않기 때문에 실행 시간에 동적으로 타입을 판단한다.
당연하게도 실행시간에 모든 데이터타입을 검사하는 과정이 포함되므로 오버헤드가 발생한다.
파이썬에서 타입 힌트와 정적 검사 도구를 제공하지만 실제로 동적 타입 검사를 실행하지 않는 방법은 존재하지 않는다.

실제로 타입 힌트와 명시적으로 데이터타입을 표기하더라도 실행시간에 큰 차이가 없다는 것을 다음 실행 결과를 통해 알 수 있다.

실행 결과 (명시적으로 리스트에 들어올 데이터의 타입을 정한 경우)




<img width="688" alt="PYTHON_static_typing" src="https://github.com/AngryOvO/linux_kernel/assets/101005580/a56c1919-f303-4583-8c95-8253d7715838">



동적 타입검사가 실행시간에 큰 영향을 주지 않아 보이지만, 후에 설명할 인터프리터에서 실행시간과의 영향에 대해 다시 알아볼 것이다.

## GC 가비지 컬렉션 

할당을 해제한 메모리들을 수집해 관리하는 기능이다.

지금까지의 테스트 코드는 이번 실험 환경의 메모리의 약 70퍼센트를 할당하고 해제하는 과정을 반복한다.
그 과정에서 가비지 컬렉션도 마찬가지로 메모리를 수집하고 정리를 반복한다.
가비지 컬렉션의 활동에 대한 오버헤드가 프로세스 실행시간에 얼마나 큰 영향을 미치는지를 알아보자.

기존 테스트 코드에서 메모리를 할당하는 시점부터 종료되는 시점까지 가비지 컬렉션을 비활성화 했을 때의 시간 차이를 보면 아래와 같다

실행 결과



<img width="657" alt="PYTHON_gc_disable" src="https://github.com/AngryOvO/linux_kernel/assets/101005580/cc0f4bd6-369e-4a33-bbba-9c70153f27d5">



실행시간에 가비지 컬렉션이 큰 영향을 주지 않는 것을 확인했다.
또한 JAVA에도 가비지 컬렉션을 내장하고 있는데 C와 속도차이가 크게 나지 않는 것에서 Python의 97초 가량의 실행시간에는 가비지 컬렉션이
큰 영향을 주지 않는다는 것을 한번 더 확인할 수 있었다.

## Numpy

지금까지의 실험에서 우리는 파이썬의 리스트를 이용해 메모리를 할당하는 시간을 측정했다.
리스트는 객체들이 흩어져 있어 각 요소를 찾는데 추가적인 오버헤드가 발생한다는 단점이 있고,
데이터를 추가하는 행동이 append()라는 함수의 호출로 이루어지기 때문에 이에 대한 오버헤드가 추가적으로 발생한다는 것을 예상할 수 있다.

즉 C와 JAVA에서 사용했던 배열보다 기본적으로 성능이 떨어진다.

파이썬에서 수치 해석 및 계산의 용도를 위해 개발된 Numpy라는 모듈이 있다.
이는 C기반의 모듈로 빠르고 효율적인 다차원 배열을 제공하는 라이브러리이다.
이는 C와 JAVA에서 사용하는 배열과 거의 유사한 형태의 자료구조를 제공하는 라이브러리이므로
이러한 Numpy를 이용해 성능을 다시 측정했다.

실험 결과 (Numpy 배열 사용)



<img width="543" alt="PYTHON_numpy_1" src="https://github.com/AngryOvO/linux_kernel/assets/101005580/40c95614-b04b-4bed-b39b-f9f9c45f398a">


Numpy의 성능이 상당히 좋다는 것을 확인할 수 있다.
Numpy의 배열과 파이썬의 리스트의 성능 차이를 비교하면

1. Numpy 배열은 C와 JAVA처럼 메모리 블록에 연속적으로 저장된다.
   이는 리스트 객체가 메모리 상에서 흩어져있어 각 요소를 찾는 오버헤드가 발생한다는 것과 차이가 있다.
   
2. Numpy 배열은 타입이 정적이다.
   이는 리스트에 다양한 타입이 저장되는 것과 다르게 동일한 데이터 타입만을 가질 수 있도록 설계되어 파이썬에서 Numpy 배열에 대한 동적 타입 검사를 수행하지 않는다.
   
3. Numpy 배열은 단위 크기가 리스트에 비해 작다
   이는 같은 크기의 메모리 블록에 더 밀도 높게 저장이 된다는 것이고, 연속적으로 저장되기 때문에 메모리의 지역성이 리스트에 비해 월등하게 높다.

그러므로 수치 해석을 위해 파이썬을 사용하는 경우에는 Numpy를 사용하는것이 리스트를 사용하는 것보다 빠른 속도와 메모리 효율성을 얻을 수 있다.

## 인터프리터

C와 JAVA와 Python이 가장 큰 차이를 보이는 특징은 Python이 인터프리터 언어라는 점이다.
애초에 Python의 동작 방식에서 다른 언어와 차이가 있다.
실행시간에 파이썬 코드가 바이트 코드로 변환되어 한 라인씩 실행한다. 

라인별로 실행이 되기 때문에 앞서 설명한 동적 타입 검사를 구현할 수 있다.

컴파일러를 통해서 컴파일 시간을 따로 갖고 실행을 하는 것이 아니기 때문에
컴파일 과정에서의 최적화를 진행할 수 없다.

예를 들면, 큰 양의 메모리 할당이나 반복문과 같이 프로그램의 실행 시간에 큰 영향을 주는 동작들은
컴파일러가 코드를 최적화 하거나 실행시의 메모리 관리의 유연함을 위한 추가적인 코드를 삽입하는 과정이 포함된다.

인터프리터에서는 이런 컴파일 과정을 거치지 않기 때문에 컴파일 시간의 최적화에 대한 이점을 가지지 못한다.

하지만 동적으로 타입을 검사하는 것과 더불어 파이썬 언어의 문법적인 이점을 활용하려면 인터프리터의 사용이 필수적이다.

파이썬 인터프리터의 동작을 자세하게 알아보기 위해서 CPython 인터프리터를 알아볼 필요가 있다.
이는 파이썬의 기본 인터프리터로 C를 통해 구현된 인터프리터이다.

가장 보편적인 인터프리터기 때문에 파이썬의 대부분의 모듈은 CPython을 기반으로 만들어진다. 앞서 설명한 Numpy가 그 예시이다.

파이썬의 다양한 인터프리터 중 JAVA와 같이 JIT 컴파일러를 사용하는 인터프리터가 존재한다.
이는 컴파일 시간이 존재하므로 JIT의 컴파일 최적화 기법을 파이썬에 적용할 수 있다.
이 인터프리터의 명칭은 PyPy3이고 파이썬으로 구현된 인터프리터이다.
PyPy3는 컴파일 시간이 존재한다고 해서 동적 타입 검사를 수행하지 못하는 것도 아니다.
자체적인 추론 기법을 사용해 변수의 타입을 추론해 이를 컴파일 시간에 반영한다.
그러므로 기존 파이썬 문법처럼 데이터타입을 명시적으로 밝히지 않아도 된다.

지금까지 실험에 사용했던 파이썬 코드를 인터프리터만 PyPy3로 변경해 실행시간을 측정했고 결과는 다음과 같다.

실험 결과 (PyPy3 인터프리터 사용)



<img width="577" alt="PYTHON_pypy" src="https://github.com/AngryOvO/linux_kernel/assets/101005580/87a7409a-f19a-4b75-bb6c-ec54ac526da4">



실행시간이 7초대로 기존 Cpython에 비해 월등하게 빠른 시간이다.
JIT 컴파일러를 사용한 효과가 실행시간에 큰 영향을 미친다는 것을 알 수 있었다.
### Cpython과 PyPy3의 메모리 할당량 별 실행시간 변화

![차트](https://github.com/AngryOvO/linux_kernel/assets/101005580/39f958b2-7b4b-4ee3-b930-ef3ae74cca87)




## 결론
메모리 할당량이 증가할 수록 Cpython은 할당 시간이 급격하게 증가하는 것을 확인할 수 있다.
PyPy3는 그에 비해 시간의 증가 폯이 완만하다.
이는 파이썬의 리스트타입을 활용한 메모리 할당의 작업에서 PyPy3가 성능이 더 뛰어나다고 볼 수 있다.
즉 특정 모듈이나 라이브러리를 사용하지 않은 상태에서 파이썬 문법에 대한 작업은 PyPy3 인터프리터를 사용하는 것이 성능 면에서 좋을 것이라는 결론이 나온다.

하지만 대부분의 파이썬 라이브러리는 Cpython을 기반으로 제작되었기 라이브러리가 PyPy3 인터프리터 환경을 지원하지 않는다면
다양한 파이썬 라이브러리를 사용할 수 없다. 또한 Cpython은 C를 통해 구현되었기 때문에 쉽게 C확장 모듈을 사용할 수 있는 환경을 제공한다.
실험에 사용했던 Numpy와 같이 수치 해석 및 계산 능력에서 리스트 타입에 비해 큰 장점을 가지는 모듈들이 많이 존재하고, 이를 쉽게 사용하기 위해서는 Cpython 인터프리터의 사용을 권장한다.
PyPy3가 성능 면에서 월등히 뛰어나지만 기존 Python의 공식 인터프리터인 Cpython의 안정성과 다양한 플랫폼 지원 등을 따라잡지 못한다면 기존 Cpython을 쉽게 대체할 수는 없다.

소형 임베디드 시스템을 기준으로 봐도 JIT 컴파일러를 포함한 PyPy3가 Cpython에 비해 무겁지만 성능 면에서 뛰어나기 때문에 프로젝트의 제약 조건, 성능 요구사항 등 여러 사항을 고려한다면 어떤 PyPy3와 Cpython들 중 어떤것이 더 좋은 인터프리터다라고 단정지을 수는 없을 것 같다.
메모리 사용량을 극한까지 사용하지 않는 이상 Cpython도 충분히 안정적인 성능을 보여주기 때문에 사용자가 프로젝트에서 추구하는 방향에 맞춰 그에 맞는 인터프리터를 선택하는 것이 가장 바람직하다.

## 의문점 및 흥미로운 점 작성 예정
