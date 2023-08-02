# GA-with-ROS

## Problem description

### 実行例
![ga_with_ros](https://github.com/Tomoya0302/GA-with-ROS/assets/23186611/f5e3e06c-389b-4483-a527-2419ecc18915)

### 問題設定

グリッド空間 ($5\times 5\times 5$) において，
グリッド空間上の任意の点からオブジェクトを搬送するとき，
ロボットの動作時間を最小化するオブジェクトの搬送座標・ロボットの配置座標と姿勢を決定します。

- 構成
    - 0.4 [m] $\times$ 0.4 [m] $\times$ 0.4 [m] のグリッド空間
    - 1台のロボット (Niryo Ned)

- 固定
    - Pick up 位置座標 (0.4, 0.4, 0.4)
    - Place 位置の $z$ 座標 ($z_t$ = 0)

- 決定変数
    - Plce 位置座標 ($x_t$, $y_t$)
    - ロボットの位置座標 ($x_r$, $y_r$, $z_r$)
    - ロボットの姿勢 (24通り...ロボットの姿勢番号については，http://kondolab.org/archive/2010/research/cadcgtext/ChapC/ChapC01.html を参照してください。)

- 評価関数
    - ロボットの動作時間最小化

- 制約条件
    - ロボットが実行可能であること

## 実行環境

- Python **2系と3系の両方を使用**
    - 3系 (3.10.7で動作確認)
    - 2系 (2.7.17で動作確認)

- ROS環境
    - ROS Melodic
    - https://docs.niryo.com/dev/ros/v4.1.1/en/source/installation/ubuntu_18.html を参照して環境構築してください。

## 実行手順

1. ターミナルで
    ```
    $ roslaunch niryo_robot_bringup desktop_rviz_simulation.launch
    ```

1. 新しいターミナルで
    ```
    $ python3 ga.py
    ```

1. 新しいターミナルで
    ```
    $ python2 ned.py
    ```

