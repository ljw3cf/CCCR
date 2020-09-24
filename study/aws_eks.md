# AWS EKS

## EKS 개요
AWS에서 제공하는 관리형 Kubenetes 서비스  
시간당 0.1$  
컨트롤러(EKS Cluster), 워커(EKS Node Group)를 따로 생성해야 함  
CloudWatch로 로그가 저장되어, ELK화 같은 모니터링 도구가 따로 필요없음

## EKS클러스터 구성방법
1. 클러스터 생성 버튼 클릭
2. 컨트롤러 노드 이름 / K8S버전* / 클러스터 서비스 역할**
3. VPC / 서브넷 / 보안그룹(인바운드, 아웃바운드 정책 고려할 것) / 퍼블릭
4. CloudWatch 로그정보 설정
5. 검토 후 생성 (생성 시 10분~15분정도 소요)


**\* EKS에서 K8S 버전 고려사항**  
K8S는 3개월마다 새로운 버전이 나온다.  
한 버전당 최대 9개월까지 서포트하였으나, 1.17부터 12개월로 확대됨.  
(12개월/3개월 = 총 4개 버전 지원)  
EKS 클러스터 구성시 서포트 기간 고려하여 버전을 선택할 것.

**\*\* EKS 클러스터 서비스 역할 생성하기**
1. IAM 접속
2. 좌측 탭의 역할 클릭
3. 역할 만들기 클릭
4. AWS 서비스 항목에서 EKS 선택
5. 하단 사용사례 선택에서 EKS-Cluster 선택 후 다음버튼 클릭
6. 권한은 자동으로 설정되어 있으므로, 다음버튼 클릭
7. 역할에 부여하고자 하는 태그를 생성 후 다음버튼 클릭
8. 역할 이름을 지정하고, 검토 후 역할 만들기 버튼 클릭


## 노드그룹 추가방법
1. 노드그룹 추가버튼 클릭
2. 노드그룹 이름 / 노드 IAM 역할 
(AmazonEKSWorkerNodePolicy/mazonEKS_CNI_PolicyAmazonEC2ContainerRegistryReadOnly) /
3. AMI 유형 / 인스턴스 유형 / 디스크 크기 / Node Group Scaling 
4. 서브넷 / SSH Key pair / 원격 접속 허용

## AWS ELK 사용하기
1. 사전설치 필요
- AWS CLI
- eksctl
- kubectl
