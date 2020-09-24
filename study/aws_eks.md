# AWS EKS

## EKS 개요
AWS에서 제공하는 관리형 Kubenetes 서비스  
시간당 0.1$  
컨트롤러(EKS Cluster), 워커(EKS Node Group)를 따로 생성해야 함  
CloudWatch로 로그가 저장되어, ELK화 같은 모니터링 도구가 따로 필요없음

## EKS클러스터 구성방법 (콘솔)
1. 클러스터 생성 버튼 클릭
2. 컨트롤러 노드 이름 / K8S버전* / 클러스터 서비스 역할**
3. VPC / 서브넷 / 보안그룹(인바운드, 아웃바운드 정책 고려할 것) / 퍼블릭
4. CloudWatch 로그정보 설정
5. 검토 후 생성 (생성 시 10분~15분정도 소요)


**\* EKS에서 K8S 버전 고려사항**  
K8S는 3개월마다 새로운 버전이 릴리즈.  
버전당 최대 9개월까지 서포트하였으나, 1.17부터 12개월로 확대.  
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


## 노드그룹 추가 (콘솔)
1. 노드그룹 추가버튼 클릭
2. 노드그룹 이름 / 노드 IAM 역할 
(AmazonEKSWorkerNodePolicy/mazonEKS_CNI_PolicyAmazonEC2ContainerRegistryReadOnly) /
3. AMI 유형 / 인스턴스 유형 / 디스크 크기 / Node Group Scaling 
4. 서브넷 / SSH Key pair / 원격 접속 허용

## EKS 클러스터 및 노드그룹 생성 (eksctl)
1. 요구 SW 설치
- AWS CLI
- eksctl*
- kubectl

2. IAM EKS 유저 생성
- 정책은 eksctl.io에서 제공하는 minimum policy에 기반하여 연결하면 좋다.
- eksctl의 minimum policy list
  - AmazonEC2FullAccess (AWS Managed Policy) 
  - AWSCloudFormationFullAccess (AWS Managed Policy) 
  - EksAllAccess (커스텀 정책\**)
  - IamLimitedAccess (커스텀 정책)  

3. AWS CLI configure

4. AWS CLI를 이용하여 EKS 클러스터 및 노드그룹 생성
<pre>
<code>
# 클러스터와 노드그룹이 동시에 생성가능하여 콘솔보다 편함!

eksctl create cluster \
--name 클러스터_이름_작성 \
--version K8S버전_작성 \
--region AWS_region_작성 \
--nodegroup-name 노드그룹_이름_작성 \
--nodes 원하는_노드수_지정 \
--nodes-min 최소_노드수_지정 \
--nodes-max 최대_노드수_지정 \
--ssh-access \
--ssh-public-key ec2_키페어_경로_지정 \
--managed
</code>
</pre>

6. 생성 확인 후 EKS 클러스터 및 노드그룹 삭제
<pre>
<code>
eksctl delete cluster -n 클러스터_이름_작성 
</code>
</pre>
**\* eksctl**  
Amazon EKS를 지원하는 공식 CLI 툴.  
GO로 제작됨.

> AWS ELK 참고사이트: https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html  
> EKS 공식사이트: https://eksctl.io/

**\*\* 커스텀 정책 생성하기**
1. IAM 서비스 선택
2. 좌측 정책 탭 클릭
3. 정책 생성 클릭
4. 시각적 편집기와 JSON 편집기를 선택할 수 있다.
5. eksctl.io에서 제공하는 정책은 json 형식이므로, JSON 편집기 클릭
6. eksctl.io에서 제공하는 정책 생성
7. \<accountid\>로 표시되는 부분은 IAM 유저 arn에서 숫자료 표기된 부분을 의미
8. 정책 검토 버튼 클릭
9. 정책 이름 설정 후 저장 클릭