# generate_from_frequencies() method 중 그리는 로직 부분 

1. 기본 설정 
   1. frquencies --> (단어, 빈도)로 구성된 리스트
   2. 빈도가 0인 단어는 제외
2. 폰트 크기 계산
   1. relative_scaling --> 단어 빈도에 비례한 폰트 크기 결정
   2. 폰트 크기는 이전 단어의 빈도와 현재 단어의 빈도를 기준으로 상대적으로 조정됨
3. 단어 회전 결정
   1. prefer_horizontal 파라미터에 따라 수평/수직 선호 결정
   2. 랜덤값에 따라 수평/수직 결정
4. 위치 찾기 및 폰트 조정
   1. font_size가 최소 폰트 크기보다 작으면 종료
   2. 각 단어에 대해 폰토 계산
   3. 텍스트가 차지하는 크기를 draw.textbox()로 구함
   4. **occupancy.sample_position()** --> 텍스트를 넣을 수 있는 공간 찾는 함수
      텍스트가 겹치지 않게 위치 조정
5. 위치가 없으면 폰트 크기 조정
   1. 공간을 찾지 못하면 텍스트 방향이나 폰트 크기를 줄이며 다시 시도
6. 이미지에 그리기
   1. draw.text()로 그림 그린다.
7. 텍스트를 그린 후 새 이미지를 갱신해 다음 텍스트가 겹치지 않도록 관리
   1. **occupancy.update()** 로 관리
8. 최종 레이아웃 계산
   1. self.layout_ = list(zip(frequencies, font_sizes, positions, orientations, colors))
   2. 최종적으로 단어, 폰트크기, 위치, 방향, 색상을 포함한 레이아웃 지정
   3. 이 레이아웃은 후속 단계에서 실제 워드 클라우드를 그릴 때 사용

## IntegralOccupancyMap 
위의 occupancy가 이 함수를 인스턴스화 한 것이다.
#### 클래스의 핵심 동작 요약
적분 영상 생성:
- 클래스 초기화 시, 이미지를 빠르게 처리하기 위한 적분 영상을 생성. (np.cumsum 사용)
공간 샘플링:
- sample_position 메서드로 적합한 공간을 무작위로 선택.
영상 업데이트:
- update 메서드로 텍스트가 배치된 후 적분 영상을 갱신하여, 사용된 공간을 반영.

**적분 영상(integral image)이란?**
적분 영상은 이미지의 각 픽셀 위치에서, 해당 위치를 포함하는 직사각형 영역의 모든 픽셀 값을 빠르게 계산할 수 있도록 한 데이터 구조<br>
특정 사각형의 합을 O(1) 시간 복잡도로 계산할 수 있으므로, 단어 구름 생성 같은 작업에서 효율적<br>


<details>
<summary>코드 보기⬇️</summary>
<div markdown="1">

``` python
    # start drawing grey image
    for word, freq in frequencies:
        if freq == 0:
            continue
        # select the font size
        rs = self.relative_scaling
        if rs != 0:
            font_size = int(round((rs * (freq / float(last_freq))
                                    + (1 - rs)) * font_size))
        if random_state.random() < self.prefer_horizontal:
            orientation = None
        else:
            orientation = Image.ROTATE_90
        tried_other_orientation = False
        while True:
            if font_size < self.min_font_size:
                # font-size went too small
                break
            # try to find a position
            font = ImageFont.truetype(self.font_path, font_size)
            # transpose font optionally
            transposed_font = ImageFont.TransposedFont(
                font, orientation=orientation)
            # get size of resulting text
            box_size = draw.textbbox((0, 0), word, font=transposed_font, anchor="lt")
            # find possible places using integral image:
            result = occupancy.sample_position(box_size[3] + self.margin,
                                                box_size[2] + self.margin,
                                                random_state)
            if result is not None:
                # Found a place
                break
            # if we didn't find a place, make font smaller
            # but first try to rotate!
            if not tried_other_orientation and self.prefer_horizontal < 1:
                orientation = (Image.ROTATE_90 if orientation is None else
                                Image.ROTATE_90)
                tried_other_orientation = True
            else:
                font_size -= self.font_step
                orientation = None

        if font_size < self.min_font_size:
            # we were unable to draw any more
            break

        x, y = np.array(result) + self.margin // 2
        # actually draw the text
        draw.text((y, x), word, fill="white", font=transposed_font)
        positions.append((x, y))
        orientations.append(orientation)
        font_sizes.append(font_size)
        colors.append(self.color_func(word, font_size=font_size,
                                        position=(x, y),
                                        orientation=orientation,
                                        random_state=random_state,
                                        font_path=self.font_path))
        # recompute integral image
        if self.mask is None:
            img_array = np.asarray(img_grey)
        else:
            img_array = np.asarray(img_grey) + boolean_mask
        # recompute bottom right
        # the order of the cumsum's is important for speed ?!
        occupancy.update(img_array, x, y)
        last_freq = freq

    self.layout_ = list(zip(frequencies, font_sizes, positions,
                            orientations, colors))
    return self
    ```

</div>
</details>